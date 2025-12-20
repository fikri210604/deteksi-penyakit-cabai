from models import Penyakit, RuleGroup

# --------------------------------------------------
# BOBOT GEJALA (0..1) - SILAKAN SESUAIKAN
# --------------------------------------------------
# Jika kode gejala tidak ada di sini, default = 1.0
BOBOT_GEJALA = {
    "G1": 0.9,
    "G2": 0.8,
    "G3": 0.8,
    "G4": 0.7,
    "G5": 0.6,
    # tambahkan sesuai kebutuhan...
}

# --------------------------------------------------
# BOBOT PENYAKIT (0..1) - SILAKAN SESUAIKAN
# --------------------------------------------------
# Jika kode penyakit tidak ada di sini, default = 1.0
BOBOT_PENYAKIT = {
    "P1": 1.0,
    "P2": 0.9,
    "P3": 0.85,
    "P4": 0.95,
    # tambahkan sesuai kebutuhan...
}


class FuzzyLogic:
    """
    Fuzzy Inference System (Tsukamoto) untuk diagnosa penyakit cabai.
    Input gejala 0..1.
    Himpunan fuzzy gejala: tidak, sedikit, sedang, banyak.
    """

    TERM_ALIASES = {
        "T": "tidak",
        "TIDAK": "tidak",
        "TIDAK_ADA": "tidak",

        "S": "sedikit",
        "SEDIKIT": "sedikit",

        "D": "sedang",
        "SEDANG": "sedang",

        "B": "banyak",
        "BANYAK": "banyak",

        # tambahan agar term admin 'sangat_banyak' dipetakan ke 'banyak'
        "SB": "banyak",
        "SANGAT_BANYAK": "banyak",
    }

    def __init__(self):
        self.groups = RuleGroup.query.all()

    # --------------------------------------------------
    # 1. FUZZIFIKASI (0..1)
    # --------------------------------------------------
    def fuzzifikasi(self, x):
        """
        Fuzzifikasi gejala (0–1)
        Konsisten dengan grafik fuzzifikasi (0–100)
        """
        x = max(0.0, min(1.0, x))

        def segitiga(x, a, b, c):
            if x <= a or x >= c:
                return 0.0
            elif a < x < b:
                return (x - a) / (b - a)
            elif b <= x < c:
                return (c - x) / (c - b)
            return 0.0

        def trapesium(x, a, b, c, d):
            # aman untuk a=b atau c=d
            if x <= a or x >= d:
                return 0.0
            if b <= x <= c:
                return 1.0
            if a < x < b:
                return (x - a) / (b - a) if b > a else 1.0
            if c < x < d:
                return (d - x) / (d - c) if d > c else 1.0
            return 0.0

        return {
            # Tidak : ada sebagai kondisi, μ = 0
            "tidak": 0.0,

            # Sedikit : trapesium kiri (0–30–45)
            "sedikit": trapesium(x, 0.0, 0.0, 0.3, 0.45),

            # Sedang : segitiga (30–45–60)
            "sedang": segitiga(x, 0.3, 0.45, 0.6),

            # Banyak : trapesium kanan (45–60–100)
            "banyak": trapesium(x, 0.45, 0.6, 1.0, 1.0),
        }



    # --------------------------------------------------
    # 1B. Ambil derajat keanggotaan berdasarkan term rule (S/D/B/T)
    # --------------------------------------------------
    def _get_membership_for_term(self, x, term):
        mu = self.fuzzifikasi(x)
        if not term:
            return 0.0

        key = term.strip().upper()
        key_norm = self.TERM_ALIASES.get(key, key.lower())
        return mu.get(key_norm, 0.0)

    # --------------------------------------------------
    # 2. EVALUASI RULE
    # --------------------------------------------------
    def evaluasi_rule(self, group, gejala_input: dict):
        alphas = []

        for cond in group.kondisi:
            kode = (cond.kode_gejala or "").strip()
            if not kode:
                continue

            term = (cond.antecedent_term or "").strip().upper()

            # Jika gejala tidak diinput user → treat as don't care
            if kode not in gejala_input:
                alphas.append(1.0)
                continue

            x = float(gejala_input[kode])
            alpha_i = self._get_membership_for_term(x, term)

            # OR-fallback: jika membership 0, jangan bunuh rule, kasih penalti
            if alpha_i == 0:
                alpha_i = 0.3

            # BOBOT GEJALA: gejala lebih penting → kontribusi lebih besar
            w_g = BOBOT_GEJALA.get(kode, 1.0)
            alpha_i *= w_g

            # Clamp ke [0,1]
            alpha_i = max(0.0, min(1.0, alpha_i))

            alphas.append(alpha_i)

        # Tidak ada kondisi ⇒ rule tidak dipakai
        if not alphas:
            return None

        alpha = min(alphas)
        if alpha <= 0.0:
            return None

        # Tsukamoto sederhana: z = alpha (bisa diganti fungsi output monotonic kalau mau)
        z = alpha
        return alpha, z, group.kode_penyakit

    # --------------------------------------------------
    # 2B. EVALUASI RULE DENGAN PENJELASAN TERPERINCI
    # --------------------------------------------------
    def evaluasi_rule_explain(self, group, gejala_input: dict):
        details = {
            "group_id": getattr(group, "id", None),
            "group_nama": getattr(group, "nama", None),
            "kode_penyakit": getattr(group, "kode_penyakit", None),
            "conditions": [],
            "alpha": None,
            "z": None,
        }

        alphas = []

        for cond in group.kondisi:
            kode = (cond.kode_gejala or "").strip()
            if not kode:
                continue

            term = (cond.antecedent_term or "").strip().upper()

            # default: don't care jika tidak diinput
            if kode not in gejala_input:
                # Jangan tampilkan di penjelasan agar tidak kebanyakan,
                # namun tetap dihitung sebagai don't care (alpha_i = 1.0)
                alphas.append(1.0)
                continue

            x = float(gejala_input[kode])
            mu_val = self._get_membership_for_term(x, term)

            catatan = None
            if mu_val == 0:
                # OR-fallback agar rule tidak langsung mati
                catatan = "membership 0, diberi penalti 0.3"
                mu_eff = 0.3
            else:
                mu_eff = mu_val

            w_g = BOBOT_GEJALA.get(kode, 1.0)
            alpha_i = max(0.0, min(1.0, mu_eff * w_g))

            details["conditions"].append({
                "kode_gejala": kode,
                "term": term,
                "x": x,
                "mu": mu_val,
                "bobot_gejala": w_g,
                "alpha_i": alpha_i,
                "catatan": catatan,
            })

            alphas.append(alpha_i)

        if not alphas:
            return None

        alpha = min(alphas)
        if alpha <= 0.0:
            return None

        z = alpha  # Tsukamoto sederhana
        details["alpha"] = alpha
        details["z"] = z
        return details

    # --------------------------------------------------
    # 3. DEFUZZIFIKASI TSUKAMOTO (per penyakit)
    # --------------------------------------------------
    def defuzzifikasi(self, rule_list):
        if not rule_list:
            return 0.0, {}

        num = {}
        den = {}

        for alpha, z, kode in rule_list:
            if alpha <= 0:
                continue

            if kode not in num:
                num[kode] = 0.0
                den[kode] = 0.0

            # BOBOT PENYAKIT diterapkan di sini
            w_p = BOBOT_PENYAKIT.get(kode, 1.0)

            num[kode] += (alpha * z) * w_p
            den[kode] += alpha * w_p

        skor_map = {}
        for kode in num:
            if den[kode] > 0:
                skor_map[kode] = num[kode] / den[kode]
            else:
                skor_map[kode] = 0.0

        z_global = max(skor_map.values()) if skor_map else 0.0

        return z_global, skor_map

    # --------------------------------------------------
    # 4. DIAGNOSA
    # --------------------------------------------------
    def diagnosa(self, gejala_input: dict, explain: bool = True):
        hasil_rules = []
        explain_rules = []

        # siapkan peta membership per gejala untuk penjelasan
        membership_inputs = {}
        if explain:
            for kode, x in (gejala_input or {}).items():
                try:
                    xv = float(x)
                except Exception:
                    continue
                membership_inputs[kode] = {
                    "x": max(0.0, min(1.0, xv)),
                    "membership": self.fuzzifikasi(xv),
                    "bobot_gejala": BOBOT_GEJALA.get(kode, 1.0),
                }

        for grp in self.groups:
            if explain:
                det = self.evaluasi_rule_explain(grp, gejala_input)
                if det and det.get("alpha", 0) > 0:
                    # Selalu masukkan ke perhitungan hasil_rules
                    hasil_rules.append((det["alpha"], det["z"], det["kode_penyakit"]))
                    # TAPI, hanya tampilkan di penjelasan jika ada kondisi yang benar-benar diinput user
                    if det.get("conditions"):
                        explain_rules.append(det)
            else:
                out = self.evaluasi_rule(grp, gejala_input)
                if out:
                    hasil_rules.append(out)

        # Defuzzifikasi (dan kumpulkan jejak per penyakit untuk penjelasan)
        z_global, skor_map = self.defuzzifikasi(hasil_rules)
        per_penyakit = {}
        if explain and hasil_rules:
            num = {}
            den = {}
            for alpha, z, kode in hasil_rules:
                if alpha <= 0:
                    continue
                w_p = BOBOT_PENYAKIT.get(kode, 1.0)
                num[kode] = num.get(kode, 0.0) + (alpha * z) * w_p
                den[kode] = den.get(kode, 0.0) + (alpha * w_p)
            for kode in set(list(num.keys()) + list(den.keys())):
                w_p = BOBOT_PENYAKIT.get(kode, 1.0)
                n = num.get(kode, 0.0)
                d = den.get(kode, 0.0)
                per_penyakit[kode] = {
                    "w_p": w_p,
                    "numerator": n,
                    "denominator": d,
                    "skor": (n / d) if d > 0 else 0.0,
                }

        if not skor_map:
            return {
                "penyakit": "Tidak Teridentifikasi",
                "nilai_fuzzy": 0.0,
                "skor_penyakit": {},
                "explanation": {
                    "inputs": membership_inputs,
                    "rules": explain_rules,
                    "defuzzifikasi": {"per_penyakit": per_penyakit, "z_global": 0.0},
                } if explain else None,
            }

        # pilih penyakit dengan skor Tsukamoto terbesar
        kode_terbaik = max(skor_map, key=skor_map.get)
        penyakit_obj = Penyakit.query.filter_by(kode_penyakit=kode_terbaik).first()

        # NORMALISASI ke "proporsi" supaya tidak gampang 100%
        total_skor = sum(skor_map.values())
        if total_skor > 0:
            nilai_fuzzy = skor_map[kode_terbaik] / total_skor
        else:
            nilai_fuzzy = 0.0

        # clamp ke [0,1]
        nilai_fuzzy = max(0.0, min(1.0, nilai_fuzzy))

        result = {
            "penyakit": penyakit_obj.nama if penyakit_obj else kode_terbaik,
            "nilai_fuzzy": nilai_fuzzy,      # ini yang kamu tampilkan sebagai %
            "skor_penyakit": skor_map,       # ini tetap nilai asli untuk grafik
        }

        if explain:
            result["explanation"] = {
                "inputs": membership_inputs,
                "rules": explain_rules,
                "defuzzifikasi": {
                    "per_penyakit": per_penyakit,
                    "z_global": z_global,
                    "total_skor_normalisasi": total_skor,
                    "kode_terpilih": kode_terbaik,
                    "nama_terpilih": penyakit_obj.nama if penyakit_obj else kode_terbaik,
                    "nilai_fuzzy_terpilih": nilai_fuzzy,
                },
            }

        return result

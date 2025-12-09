from models import Penyakit, RuleGroup


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
        x = max(0.0, min(1.0, x))

        # -----------------
        # TIDAK ADA
        # -----------------
        if x <= 0.0:
            tidak = 1.0
        elif x <= 0.2:
            tidak = (0.2 - x) / 0.2
        else:
            tidak = 0.0

        # -----------------
        # SEDIKIT
        # -----------------
        if x <= 0.0 or x >= 0.6:
            sedikit = 0.0
        elif 0.0 < x <= 0.4:
            sedikit = (x - 0.0) / 0.4
        elif 0.4 < x < 0.6:
            sedikit = (0.6 - x) / 0.2
        else:
            sedikit = 0.0

        # -----------------
        # SEDANG
        # -----------------
        if x <= 0.3 or x >= 0.7:
            sedang = 0.0
        elif 0.3 < x <= 0.5:
            sedang = (x - 0.3) / 0.2
        elif 0.5 < x < 0.7:
            sedang = (0.7 - x) / 0.2
        else:
            sedang = 0.0

        # -----------------
        # BANYAK
        # -----------------
        if x <= 0.5:
            banyak = 0.0
        elif 0.5 < x <= 0.7:
            banyak = (x - 0.5) / 0.2
        else:
            banyak = 1.0

        return {
            "tidak": tidak,
            "sedikit": sedikit,
            "sedang": sedang,
            "banyak": banyak,
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

            if kode not in gejala_input:
                if term in ("T", "TIDAK", "TIDAK_ADA"):
                    alphas.append(1.0)
                    continue
                return None


            x = float(gejala_input[kode])

            alpha_i = self._get_membership_for_term(x, cond.antecedent_term)
            alphas.append(alpha_i)

        # Tidak ada kondisi yang dipakai → rule tidak dipakai
        if not alphas:
            return None

        alpha = min(alphas)
        if alpha <= 0.0:
            return None

        z = alpha  # Tsukamoto: μ(z) = z
        return alpha, z, group.kode_penyakit


    # --------------------------------------------------
    # 3. DEFUZZIFIKASI TSUKAMOTO
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

            num[kode] += alpha * z
            den[kode] += alpha

        skor_map = {}
        for kode in num:
            skor_map[kode] = num[kode] / den[kode] if den[kode] > 0 else 0.0

        z_global = max(skor_map.values()) if skor_map else 0.0

        return z_global, skor_map

    # --------------------------------------------------
    # 4. DIAGNOSA
    # --------------------------------------------------
    def diagnosa(self, gejala_input: dict):

        hasil_rules = []

        for grp in self.groups:
            out = self.evaluasi_rule(grp, gejala_input)
            if out:
                hasil_rules.append(out)

        _, skor_map = self.defuzzifikasi(hasil_rules)

        if not skor_map:
            return {
                "penyakit": "Tidak Teridentifikasi",
                "nilai_fuzzy": 0.0,
                "skor_penyakit": {},
            }

        kode_terbaik = max(skor_map, key=skor_map.get)
        penyakit_obj = Penyakit.query.filter_by(kode_penyakit=kode_terbaik).first()

        return {
            "penyakit": penyakit_obj.nama if penyakit_obj else kode_terbaik,
            "nilai_fuzzy": skor_map[kode_terbaik],
            "skor_penyakit": skor_map,
        }

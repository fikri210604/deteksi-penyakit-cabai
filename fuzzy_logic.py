from models import Penyakit, RuleGroup


class FuzzyLogic:
    """
    Fuzzy Inference System (Sugeno) sederhana untuk diagnosa penyakit cabai.
    - 3 himpunan fuzzy: sedikit, sedang, banyak
    - Konsekuen Sugeno berupa konstanta z di skala 0..1
    """

    # Nilai konsekuen (z) Sugeno untuk setiap term output
    Z = {
        "sedikit": 0.2,
        "sedang": 0.5,
        "banyak": 0.8,
    }

    def __init__(self):
        # Ambil seluruh rule group dari database
        self.groups = RuleGroup.query.all()

    # --------------------------------------------------
    # 1. FUZZIFIKASI
    # --------------------------------------------------
    def fuzzifikasi(self, x: float) -> dict:
        """
        Mengubah nilai crisp (0..1) menjadi derajat keanggotaan
        untuk 3 himpunan fuzzy: sedikit, sedang, banyak.
        """
        x = max(0.0, min(1.0, float(x)))

        # sedikit: tinggi di dekat 0, turun ke 0 saat x >= 0.4
        if x <= 0.4:
            sedikit = 1.0 - (x / 0.4)
        else:
            sedikit = 0.0

        # sedang: segitiga sekitar 0.5 (0.3–0.7)
        if 0.3 <= x <= 0.5:
            sedang = (x - 0.3) / 0.2
        elif 0.5 < x <= 0.7:
            sedang = (0.7 - x) / 0.2
        else:
            sedang = 0.0

        # banyak: naik mulai 0.6, penuh di 1.0
        if x >= 0.6:
            if x < 1.0:
                banyak = (x - 0.6) / 0.4
            else:
                banyak = 1.0
        else:
            banyak = 0.0

        return {
            "sedikit": max(0.0, min(1.0, sedikit)),
            "sedang": max(0.0, min(1.0, sedang)),
            "banyak": max(0.0, min(1.0, banyak)),
        }

    # --------------------------------------------------
    # 2. EVALUASI SATU RULE-GROUP (INFERENSI)
    # --------------------------------------------------
    def evaluasi_rule(self, group, gejala_input: dict):
        """
        Menghitung derajat kebenaran (alpha) untuk satu rule-group.
        - Jika ada gejala dalam rule yang tidak diisi user → rule di-skip (None).
        - alpha = min(µ_1, µ_2, ..., µ_n)   (operator AND = MIN)
        """
        alphas = []

        for cond in group.kondisi:
            kode = cond.kode_gejala

            # Jika gejala yang menjadi syarat rule tidak diisi user → rule tidak aktif
            if kode not in gejala_input:
                return None

            x = gejala_input[kode]           # nilai crisp 0..1 dari user
            mu = self.fuzzifikasi(x)         # derajat keanggotaan
            alpha_i = mu.get(cond.antecedent_term, 0.0)
            alphas.append(alpha_i)

        if not alphas:
            return None

        alpha = min(alphas)  # AND menggunakan MIN
        if alpha <= 0.0:
            return None      # rule tidak berkontribusi

        # Ambil nilai konsekuen (z) Sugeno
        if group.z_override is not None:
            z = float(group.z_override)
        else:
            z = self.Z.get(group.consequent_term, 0.5)

        return alpha, z, group.kode_penyakit

    # --------------------------------------------------
    # 3. DEFUZZIFIKASI (WEIGHTED AVERAGE)
    # --------------------------------------------------
    def defuzzifikasi(self, rule_list):
        """
        Menghitung:
        - z_global  : nilai fuzzy gabungan semua rule (0..1)
        - skor_map  : skor per penyakit {kode_penyakit: skor (0..1)}

        Rumus per penyakit:
            skor_k = Σ(alpha_i * z_i) / Σ alpha_i
        Rumus global:
            z_global = Σ(alpha_i * z_i) / Σ alpha_i  (semua rule)
        """
        if not rule_list:
            return 0.0, {}

        # Akumulator global dan per penyakit
        total_alpha = 0.0
        total_alpha_z = 0.0

        num_per_penyakit = {}  # Σ(alpha*z) per penyakit
        den_per_penyakit = {}  # Σ(alpha)   per penyakit

        for alpha, z, kode in rule_list:
            if alpha <= 0.0:
                continue

            alpha_z = alpha * z

            # global
            total_alpha += alpha
            total_alpha_z += alpha_z

            # per penyakit
            if kode not in num_per_penyakit:
                num_per_penyakit[kode] = 0.0
                den_per_penyakit[kode] = 0.0

            num_per_penyakit[kode] += alpha_z
            den_per_penyakit[kode] += alpha

        if total_alpha == 0.0:
            return 0.0, {}

        z_global = total_alpha_z / total_alpha

        # skor per penyakit (0..1)
        skor_map = {}
        for kode in num_per_penyakit:
            if den_per_penyakit[kode] > 0:
                skor_map[kode] = num_per_penyakit[kode] / den_per_penyakit[kode]
            else:
                skor_map[kode] = 0.0

        return z_global, skor_map

    # --------------------------------------------------
    # 4. DIAGNOSA
    # --------------------------------------------------
    def diagnosa(self, gejala_input: dict):
        """
        gejala_input: dict {"G1": 0.2, "G3": 0.7, ...} nilai 0..1
        Mengembalikan:
        - penyakit terbaik (nama)
        - nilai_fuzzy (skor 0..1 untuk penyakit terbaik)
        - skor_penyakit: dict {kode_penyakit: skor 0..1}
        """
        hasil_rules = []

        # Evaluasi semua rule-group
        for grp in self.groups:
            out = self.evaluasi_rule(grp, gejala_input)
            if out:
                hasil_rules.append(out)

        # Defuzzifikasi
        _, skor_map = self.defuzzifikasi(hasil_rules)

        if not skor_map:
            return {
                "penyakit": "Tidak Teridentifikasi",
                "nilai_fuzzy": 0.0,
                "skor_penyakit": {},
            }

        # Ambil penyakit dengan skor tertinggi
        kode_terbaik = max(skor_map, key=skor_map.get)
        penyakit_obj = Penyakit.query.filter_by(kode_penyakit=kode_terbaik).first()

        nama = penyakit_obj.nama if penyakit_obj else kode_terbaik
        skor_terbaik = skor_map[kode_terbaik]  # 0..1

        return {
            "penyakit": nama,
            "nilai_fuzzy": skor_terbaik,   # 0..1 → kalikan 100 di tampilan
            "skor_penyakit": skor_map,     # semua skor penyakit (0..1)
        }

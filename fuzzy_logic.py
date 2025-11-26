import numpy as np
from models import Rule, Penyakit, Gejala, RuleGroup

class FuzzyLogic:
    def __init__(self):
        self.rules = Rule.query.all()
        self.rule_groups = RuleGroup.query.all()
        self.penyakit = Penyakit.query.all()
        self.gejala = Gejala.query.all()
        self.sugeno_z_map = {
            'rendah': 0.2,
            'sedang': 0.5,
            'tinggi': 0.8,
        }

    def _tri(self, x: float, a: float, b: float, c: float) -> float:
        if x <= a or x >= c:
            return 0.0
        if x == b:
            return 1.0
        if x < b:
            return (x - a) / (b - a)
        return (c - x) / (c - b)

    def _trap(self, x: float, a: float, b: float, c: float, d: float) -> float:
        if x <= a or x >= d:
            return 0.0
        if b <= x <= c:
            return 1.0
        if a < x < b:
            return (x - a) / (b - a)
        if c < x < d:
            return (d - x) / (d - c)
        return 0.0

    def fuzzifikasi(self, x: float):
        """Fuzzifikasi domain 0..1 untuk 5 istilah antecedent."""
        x = max(0.0, min(1.0, float(x)))

        mu_tidak = self._trap(x, 0.0, 0.0, 0.05, 0.2)
        mu_sedikit = self._tri(x, 0.1, 0.25, 0.4)
        mu_sedang = self._tri(x, 0.3, 0.5, 0.7)
        mu_banyak = self._tri(x, 0.6, 0.75, 0.9)
        mu_sangat = self._trap(x, 0.8, 0.95, 1.0, 1.0)

        mu_rendah = max(mu_tidak, mu_sedikit)
        mu_parah = max(mu_banyak, mu_sangat)

        return {
            'tidak_ada': mu_tidak,
            'sedikit': mu_sedikit,
            'sedang': mu_sedang,
            'banyak': mu_banyak,
            'sangat_banyak': mu_sangat,
            # alias 3-level untuk rule sederhana
            'rendah': mu_rendah,
            'parah': mu_parah,
        }


    def inferensi_rules_sederhana(self, gejala_input: dict):
        hasil_rule = []
        for rule in self.rules:
            if not rule.tipe_fuzzy:
                continue
            if rule.kode_gejala not in gejala_input:
                continue
            x = gejala_input[rule.kode_gejala]
            mu = self.fuzzifikasi(x)
            alpha = mu.get(rule.tipe_fuzzy, 0.0)
            if alpha <= 0:
                continue
            z = self.hitung_z(rule.tipe_fuzzy, alpha)
            hasil_rule.append((alpha, z, rule.kode_penyakit))
        return hasil_rule

    def _consequent_sugeno(self, term: str) -> float:
        return float(self.sugeno_z_map.get(term, 0.5))

    def inferensi_groups_sugeno(self, gejala_input: dict):
        hasil = []
        for grp in self.rule_groups:
            if not getattr(grp, 'aktif', True):
                continue
            kondisi = getattr(grp, 'kondisi', [])
            if not kondisi:
                continue
            alphas = []
            for cond in kondisi:
                kode = cond.kode_gejala
                if kode not in gejala_input:
                    continue
                x = gejala_input.get(kode, 0.0)
                mu = self.fuzzifikasi(x)
                alphas.append(mu.get(cond.antecedent_term, 0.0))
            if not alphas:
                continue
            alpha = min(alphas)
            try:
                w = float(getattr(grp, 'bobot', 1.0) or 1.0)
            except Exception:
                w = 1.0
            alpha = max(0.0, min(1.0, alpha * w))
            if alpha <= 0:
                continue
            z = None
            try:
                z_override = getattr(grp, 'z_override', None)
                if z_override is not None:
                    z = float(z_override)
            except Exception:
                z = None
            if z is None:
                z = self._consequent_sugeno(grp.consequent_term)
            hasil.append((alpha, z, grp.kode_penyakit))
        return hasil

    def hitung_z(self, tipe: str, alpha: float):
        # Konsekuen pada domain output 0..1
        if tipe == 'rendah':
            return 0.0 + alpha * 0.3
        elif tipe == 'sedang':
            return 0.3 + alpha * 0.4
        else:
            return 0.7 + alpha * 0.3

    def defuzzifikasi(self, hasil_rule):
        if not hasil_rule:
            return 0, {}

        alpha_list = []
        z_list = []
        per_penyakit = {}

        for alpha, z, kode_penyakit in hasil_rule:
            alpha_list.append(alpha)
            z_list.append(z)

            if kode_penyakit not in per_penyakit:
                per_penyakit[kode_penyakit] = []

            per_penyakit[kode_penyakit].append((alpha, z))

        z_global = sum(a * z for a, z in zip(alpha_list, z_list)) / sum(alpha_list)

        skor_penyakit = { kode: round(sum(a * z for a, z in lst) / sum(a for a, _ in lst), 3) for kode, lst in per_penyakit.items()}

        return round(z_global, 3), skor_penyakit


    def diagnosa(self, gejala_input: dict):
        """
        gejala_input format:
        {
            "G1": 7.5,
            "G3": 5,
            "G10": 9
        }
        """
        hasil_group = self.inferensi_groups_sugeno(gejala_input)
        if hasil_group:
            z_final, skor_penyakit = self.defuzzifikasi(hasil_group)
        else:
            z_final, skor_penyakit = 0.0, {}

        if skor_penyakit:
            kode_terbaik = max(skor_penyakit, key=skor_penyakit.get)
            penyakit_obj = Penyakit.query.filter_by(kode_penyakit=kode_terbaik).first()
            nama_penyakit = penyakit_obj.nama if penyakit_obj else kode_terbaik
        else:
            nama_penyakit = "Tidak diketahui"

        return {'penyakit': nama_penyakit,'nilai_fuzzy': z_final,'skor_penyakit': skor_penyakit}
        

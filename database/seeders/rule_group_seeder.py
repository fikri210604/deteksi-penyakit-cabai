from main import app
from models import db, RuleGroup, RuleCondition, Penyakit, Gejala


def run_rule_group_seeder():
    with app.app_context():
        print("--- Memulai Seeding Rule Group (Tsukamoto) ---")

        DATA_RULES = [

            # P1 – Rebah Semai
            {
                'nama': 'RG-P1-1',
                'kode_penyakit': 'P1',
                'consequent_term': 'tinggi',
                'bobot': 1.0,
                'aktif': True,
                'kondisi': [
                    ('G1', 'banyak'),
                    ('G2', 'sedang'),
                    ('G9', 'banyak'),
                ]
            },

            # P2 – Layu Bakteri
            {
                'nama': 'RG-P2-1',
                'kode_penyakit': 'P2',
                'consequent_term': 'tinggi',
                'bobot': 1.0,
                'aktif': True,
                'kondisi': [
                    ('G4', 'banyak'),
                    ('G6', 'sedang'),
                    ('G7', 'banyak'),
                ]
            },

            # P3 – Layu Fusarium
            {
                'nama': 'RG-P3-1',
                'kode_penyakit': 'P3',
                'consequent_term': 'tinggi',
                'bobot': 1.0,
                'aktif': True,
                'kondisi': [
                    ('G4', 'sedang'),
                    ('G5', 'banyak'),
                    ('G9', 'banyak'),
                ]
            },

            # P4 – Busuk Phytophthora
            {
                'nama': 'RG-P4-1',
                'kode_penyakit': 'P4',
                'consequent_term': 'tinggi',
                'bobot': 1.0,
                'aktif': True,
                'kondisi': [
                    ('G8', 'banyak'),
                    ('G10', 'banyak'),
                    ('G11', 'sedang'),
                ]
            },

            # P5 – Kuncup Daun
            {
                'nama': 'RG-P5-1',
                'kode_penyakit': 'P5',
                'consequent_term': 'sedang',
                'bobot': 0.9,
                'aktif': True,
                'kondisi': [
                    ('G12', 'banyak'),
                    ('G13', 'sedikit'),
                ]
            },

            # P6 – Bercak Cercospora
            {
                'nama': 'RG-P6-1',
                'kode_penyakit': 'P6',
                'consequent_term': 'sedang',
                'bobot': 1.0,
                'aktif': True,
                'kondisi': [
                    ('G14', 'sedang'),
                    ('G16', 'banyak'),
                    ('G17', 'sedikit'),
                ]
            },

            # P7 – Bercak Bakteri
            {
                'nama': 'RG-P7-1',
                'kode_penyakit': 'P7',
                'consequent_term': 'tinggi',
                'bobot': 1.0,
                'aktif': True,
                'kondisi': [
                    ('G8', 'sedang'),
                    ('G18', 'banyak'),
                    ('G21', 'sedikit'),
                ]
            },

            # P8 – Antraknosa
            {
                'nama': 'RG-P8-1',
                'kode_penyakit': 'P8',
                'consequent_term': 'tinggi',
                'bobot': 1.0,
                'aktif': True,
                'kondisi': [
                    ('G11', 'banyak'),
                    ('G19', 'banyak'),
                    ('G20', 'sedang'),
                ]
            },

            # P9 – Virus Gemini
            {
                'nama': 'RG-P9-1',
                'kode_penyakit': 'P9',
                'consequent_term': 'tinggi',
                'bobot': 0.9,
                'aktif': True,
                'kondisi': [
                    ('G15', 'banyak'),
                    ('G17', 'sedang'),
                    ('G23', 'banyak'),
                ]
            },

            # P10 – Embun Tepung
            {
                'nama': 'RG-P10-1',
                'kode_penyakit': 'P10',
                'consequent_term': 'sedang',
                'bobot': 0.9,
                'aktif': True,
                'kondisi': [
                    ('G16', 'sedikit'),
                    ('G24', 'banyak'),
                    ('G15', 'sedang'),
                ]
            },

        ]

        created = 0
        for ex in DATA_RULES:
            # pastikan penyakit ada
            p = Penyakit.query.filter_by(kode_penyakit=ex['kode_penyakit']).first()
            if not p:
                print(f"[SKIP] Penyakit {ex['kode_penyakit']} belum ada.")
                continue

            # cek nama unik
            exists = RuleGroup.query.filter_by(nama=ex['nama']).first()
            if exists:
                print(f"[-] Group {ex['nama']} sudah ada, skip.")
                continue

            grp = RuleGroup(
                nama=ex['nama'],
                kode_penyakit=ex['kode_penyakit'],
                consequent_term=ex['consequent_term'],
                bobot=ex['bobot'],
                aktif=ex['aktif']
            )
            db.session.add(grp)
            db.session.flush()

            for kode_gjl, term in ex['kondisi']:
                g = Gejala.query.filter_by(kode=kode_gjl).first()
                if not g:
                    print(f"[SKIP] Gejala {kode_gjl} tidak ditemukan.")
                    continue
                cond = RuleCondition(group_id=grp.id, kode_gejala=kode_gjl, antecedent_term=term)
                db.session.add(cond)

            created += 1

        db.session.commit()
        print(f"--- Selesai! {created} rule group baru ditambahkan. ---\n")


if __name__ == '__main__':
    run_rule_group_seeder()

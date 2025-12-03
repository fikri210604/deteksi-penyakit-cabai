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
        'consequent_term': 'banyak',
        'bobot': 1.0,
        'aktif': True,
        'kondisi': [
            ('G1', 'banyak'),
            ('G8', 'banyak'),
            ('G11', 'sedang')
        ]
    },

    # P2 – Layu Bakteri
    {
        'nama': 'RG-P2-1',
        'kode_penyakit': 'P2',
        'consequent_term': 'banyak',
        'bobot': 1.0,
        'aktif': True,
        'kondisi': [
            ('G5', 'banyak'),
            ('G11', 'banyak'),
            ('G7', 'sedang')
        ]
    },

    # P3 – Layu Fusarium
    {
        'nama': 'RG-P3-1',
        'kode_penyakit': 'P3',
        'consequent_term': 'banyak',
        'bobot': 1.0,
        'aktif': True,
        'kondisi': [
            ('G5', 'sedang'),
            ('G11', 'banyak'),
            ('G9', 'sedang')
        ]
    },

    # P4 – Busuk Phytophthora
    {
        'nama': 'RG-P4-1',
        'kode_penyakit': 'P4',
        'consequent_term': 'banyak',
        'bobot': 1.0,
        'aktif': True,
        'kondisi': [
            ('G7', 'banyak'),
            ('G8', 'sedang'),
            ('G10', 'banyak')
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
            ('G4', 'banyak'),
            ('G6', 'sedang')
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
            ('G1', 'sedang'),
            ('G3', 'banyak'),
            ('G8', 'sedikit')
        ]
    },

    # P7 – Bercak Bakteri
    {
        'nama': 'RG-P7-1',
        'kode_penyakit': 'P7',
        'consequent_term': 'banyak',
        'bobot': 1.0,
        'aktif': True,
        'kondisi': [
            ('G2', 'banyak'),
            ('G3', 'sedang')
        ]
    },

    # P8 – Antraknosa
    {
        'nama': 'RG-P8-1',
        'kode_penyakit': 'P8',
        'consequent_term': 'banyak',
        'bobot': 1.0,
        'aktif': True,
        'kondisi': [
            ('G7', 'banyak'),
            ('G10', 'sedang')
        ]
    },

    # P9 – Virus Gemini
    {
        'nama': 'RG-P9-1',
        'kode_penyakit': 'P9',
        'consequent_term': 'banyak',
        'bobot': 0.9,
        'aktif': True,
        'kondisi': [
            ('G4', 'banyak'),
            ('G5', 'banyak'),
            ('G12', 'banyak')
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
            ('G5', 'sedikit'),
            ('G1', 'sedikit')
        ]
    }
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

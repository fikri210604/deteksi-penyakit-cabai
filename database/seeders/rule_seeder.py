# database/seeders/rule_seeder.py

from main import app
from models import db, Rule, Penyakit, Gejala


DATA_RULE = [
    {
        "kode_penyakit": "P3",
        "nama_penyakit": "Layu Fusarium",
        "gejala": ["G1", "G2", "G3", "G4", "G6"]
    },
    {
        "kode_penyakit": "P8",
        "nama_penyakit": "Antraknosa", 
        "gejala": ["G3", "G8", "G10"]
    },
    {
        "kode_penyakit": "P9",
        "nama_penyakit": "Virus Gemini",  
        "gejala": ["G3", "G6", "G10"]
    },
    {
        "kode_penyakit": "P2",
        "nama_penyakit": "Layu Bakteri",
        "gejala": ["G5", "G7", "G10"]
    },
    {
        "kode_penyakit": "P1",
        "nama_penyakit": "Rebah Semai",
        "gejala": ["G5", "G9"]
    },
]



def run_rule_seeder():
    with app.app_context():
        print("--- Memulai Seeding Rule Base ---")

        inserted = 0

        for item in DATA_RULE:
            kode_penyakit = item["kode_penyakit"]
            gejala_list = item["gejala"]

            # pastikan penyakitnya ada
            penyakit = Penyakit.query.filter_by(kode_penyakit=kode_penyakit).first()
            if not penyakit:
                print(f"[SKIP] Penyakit {kode_penyakit} belum ada di tabel penyakit.")
                continue

            for kode_gejala in gejala_list:
                # pastikan gejala ada
                gejala = Gejala.query.filter_by(kode=kode_gejala).first()
                if not gejala:
                    print(f"[SKIP] Gejala {kode_gejala} belum ada di tabel gejala.")
                    continue

                # cek apakah rule sudah ada
                exists = Rule.query.filter_by(
                    kode_penyakit=kode_penyakit,
                    kode_gejala=kode_gejala
                ).first()

                if exists:
                    print(f"[-] Rule {kode_penyakit} - {kode_gejala} sudah ada, skip.")
                    continue

                new_rule = Rule(
                    kode_penyakit=kode_penyakit,
                    kode_gejala=kode_gejala,
                    tipe_fuzzy='sedang'
                )
                db.session.add(new_rule)
                inserted += 1
                print(f"[+] Tambah Rule: {kode_penyakit} -> {kode_gejala}")

        db.session.commit()
        print(f"--- Selesai! {inserted} rule baru ditambahkan. ---\n")


if __name__ == "__main__":
    run_rule_seeder()

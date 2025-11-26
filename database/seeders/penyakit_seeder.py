from main import app
from models import db, Penyakit

# Data Penyakit & Solusi
DATA_PENYAKIT = [
    {"kode": "P1", "nama": "Rebah Semai"},
    {"kode": "P2", "nama": "Layu Bakteri"},
    {"kode": "P3", "nama": "Layu Fusarium"},
    {"kode": "P4", "nama": "Busuk Phythophtora"},
    {"kode": "P5", "nama": "Kuncup Daun"},
    {"kode": "P6", "nama": "Bercak Cercospora"},
    {"kode": "P7", "nama": "Bercak Bakteri"},
    {"kode": "P8", "nama": "Antraknosa"},
    {"kode": "P9", "nama": "Virus Gemini"},
    {"kode": "P10", "nama": "Embun Tepung"}
]

def run_penyakit_seeder():
    with app.app_context():
        print("--- Memulai Seeding Penyakit ---")
        
        count = 0
        for p in DATA_PENYAKIT:
            exists = Penyakit.query.filter_by(kode_penyakit=p['kode']).first()
            if not exists:
                new_p = Penyakit(
                    kode_penyakit=p['kode'],
                    nama=p['nama']
                )
                db.session.add(new_p)
                count += 1
                print(f"[+] Menambahkan: {p['kode']} - {p['nama']}")
            else:
                print(f"[-] Skip (Sudah ada): {p['kode']}")

        db.session.commit()
        print(f"--- Selesai! {count} penyakit baru ditambahkan. ---\n")

if __name__ == "__main__":
    run_penyakit_seeder()

from main import app
from models import db, Gejala

DATA_GEJALA = [
    {"kode": "G1",  "nama": "Bercak pada daun"},
    {"kode": "G2",  "nama": "Daun sobek"},
    {"kode": "G3",  "nama": "Bercak coklat"},
    {"kode": "G4",  "nama": "Daun menggulung"},
    {"kode": "G5",  "nama": "Daun menguning"},
    {"kode": "G6",  "nama": "Daun menebal"},
    {"kode": "G7",  "nama": "Buah keriput"},
    {"kode": "G8",  "nama": "Daun gugur"},
    {"kode": "G9",  "nama": "Tulang daun menonjol"},
    {"kode": "G10","nama": "Bunga rontok"},
    {"kode": "G11","nama": "Tanaman kerdil"},
    {"kode": "G12","nama": "Kutu kebul"},
]


def run_gejala_seeder():
    with app.app_context():
        print("--- Memulai Seeding Gejala (Tsukamoto – Skripsi) ---")
        
        count = 0
        for g in DATA_GEJALA:
            exists = Gejala.query.filter_by(kode=g['kode']).first()
            if not exists:
                new_g = Gejala(kode=g['kode'], nama=g['nama'])
                db.session.add(new_g)
                count += 1
                print(f"[+] Menambahkan: {g['kode']} - {g['nama']}")
            else:
                print(f"[-] Skip (Sudah ada): {g['kode']}")

        db.session.commit()
        print(f"--- Selesai! {count} gejala baru ditambahkan. ---\n")


if __name__ == "__main__":
    run_gejala_seeder()

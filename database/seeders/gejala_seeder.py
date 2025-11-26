from main import app
from models import db, Gejala

# Data Gejala dari Jurnal
DATA_GEJALA = [
    {"kode": "G1", "nama": "Bercak kering pada daun"},
    {"kode": "G2", "nama": "Bercak daun bulat dan sobek"},
    {"kode": "G3", "nama": "Bercak berwarna coklat abu-abu"},
    {"kode": "G4", "nama": "Daun menggulung ke arah bawah"},
    {"kode": "G5", "nama": "Daun menguning"},
    {"kode": "G6", "nama": "Daun hijau pekat mengkilat"},
    {"kode": "G7", "nama": "Buah mengering dan keriput (ada bercak hitam/membusuk)"},
    {"kode": "G8", "nama": "Daun gugur"},
    {"kode": "G9", "nama": "Tulang daun menonjol / menebal"},
    {"kode": "G10", "nama": "Bakal buah dan bunga gugur"},
    {"kode": "G11", "nama": "Tanaman kerdil"},
    {"kode": "G12", "nama": "Ditemukan kutu kebul (Bemisia tabaci)"}
]


def run_gejala_seeder():
    with app.app_context():
        print("--- Memulai Seeding Gejala ---")
        
        count = 0
        for g in DATA_GEJALA:
            # Cek apakah gejala sudah ada biar tidak duplikat
            exists = Gejala.query.filter_by(kode=g['kode']).first()
            if not exists:
                new_g = Gejala(
                    kode=g['kode'],
                    nama=g['nama']
                )
                db.session.add(new_g)
                count += 1
                print(f"[+] Menambahkan: {g['kode']} - {g['nama']}")
            else:
                print(f"[-] Skip (Sudah ada): {g['kode']}")

        db.session.commit()
        print(f"--- Selesai! {count} gejala baru ditambahkan. ---\n")

if __name__ == "__main__":
    run_gejala_seeder()

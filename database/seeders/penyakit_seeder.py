from main import app
from models import db, Penyakit

# Data Penyakit sesuai Tabel 5.2 skripsi
# P1 Antraknosa
# P2 Cercospora
# P3 Virus Gemini
# P4 Penyakit Kerupuk
DATA_PENYAKIT = [
    {
        "kode": "P1",
        "nama": "Antraknosa",
        "deskripsi": "Buah cabai menunjukkan bercak cekung berwarna hitam, menyebabkan busuk kering. Disebabkan jamur Colletotrichum capsici.",
        "solusi": "Buang buah terinfeksi, jaga sanitasi kebun, gunakan fungisida sesuai anjuran (misalnya berbahan aktif tembaga/azoksistrobin)."
    },
    {
        "kode": "P2",
        "nama": "Cercospora",
        "deskripsi": "Penyakit bercak daun akibat jamur Cercospora capsici, bercak abu-abu dengan tepi lebih gelap yang menyebabkan daun mengering dan gugur.",
        "solusi": "Gunakan fungisida kontak (mis. mankozeb/klorotalonil), lakukan sanitasi daun terinfeksi, dan perbaiki sirkulasi udara tanaman."
    },
    {
        "kode": "P3",
        "nama": "Virus Gemini",
        "deskripsi": "Daun keriting, menebal, belang hijau-kuning. Disebabkan oleh Gemini virus yang ditularkan kutu kebul (Bemisia tabaci).",
        "solusi": "Kendalikan kutu kebul (perangkap kuning, insektisida sistemik), gunakan benih sehat dan varietas toleran, serta cabut tanaman terinfeksi berat."
    },
    {
        "kode": "P4",
        "nama": "Penyakit Kerupuk",
        "deskripsi": "Buah tampak mengering, keriput seperti kerupuk; sering terkait kombinasi gejala fisiologis dan patogen tertentu.",
        "solusi": "Perbaiki pemupukan dan irigasi, jaga kebersihan lahan, dan lakukan pengendalian penyakit pendukung sesuai rekomendasi pakar."
    },
]

def run_penyakit_seeder():
    with app.app_context():
        print("--- Memulai Seeding Penyakit (Versi Skripsi Tsukamoto) ---")
        
        count = 0
        for p in DATA_PENYAKIT:
            exists = Penyakit.query.filter_by(kode_penyakit=p['kode']).first()
            if not exists:
                new_p = Penyakit(
                    kode_penyakit=p['kode'],
                    nama=p['nama'],
                    # kalau model-mu punya kolom deskripsi & solusi, isi di sini:
                    # deskripsi=p['deskripsi'],
                    # solusi=p['solusi'],
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

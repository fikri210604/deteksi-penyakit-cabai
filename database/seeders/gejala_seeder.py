from main import app
from models import db, Gejala

# Data Gejala dari Jurnal
DATA_GEJALA = [
    {
        "kode": "G1",
        "nama": "Bercak kering pada daun",
        "deskripsi": "Daun memiliki bercak berwarna coklat hingga kehitaman yang tampak kering. Merupakan gejala awal infeksi jamur penyebab bercak daun."
    },
    {
        "kode": "G2",
        "nama": "Bercak bulat / daun sobek",
        "deskripsi": "Daun menunjukkan bercak berbentuk bulat yang dapat menyebabkan jaringan daun robek. Umum terjadi pada penyakit bercak daun berat."
    },
    {
        "kode": "G3",
        "nama": "Bercak coklat abu-abu pada daun",
        "deskripsi": "Bercak berwarna coklat keabu-abuan yang semakin meluas. Gejala khas infeksi jamur seperti Cercospora atau Alternaria."
    },
    {
        "kode": "G4",
        "nama": "Daun menggulung ke bawah",
        "deskripsi": "Daun melengkung dan menggulung ke arah bawah. Gejala khas serangan virus kuning keriting yang dibawa kutu kebul."
    },
    {
        "kode": "G5",
        "nama": "Daun menguning",
        "deskripsi": "Daun berubah warna menjadi kuning, baik sebagian maupun keseluruhan. Berkaitan dengan serangan virus atau gangguan fotosintesis."
    },
    {
        "kode": "G6",
        "nama": "Daun hijau pekat mengkilat",
        "deskripsi": "Daun tampak berwarna hijau gelap, tebal, dan mengkilat. Gejala umum infeksi gemini virus yang menyebabkan perubahan struktur daun."
    },
    {
        "kode": "G7",
        "nama": "Buah keriput / bercak hitam / busuk",
        "deskripsi": "Buah menunjukkan keriput, bercak hitam, atau pembusukan cekung. Gejala utama penyakit antraknosa pada buah cabai."
    },
    {
        "kode": "G8",
        "nama": "Daun gugur",
        "deskripsi": "Daun rontok sebelum waktunya akibat infeksi jamur atau kerusakan jaringan daun. Sering menyertai bercak daun."
    },
    {
        "kode": "G9",
        "nama": "Tulang daun menonjol / menebal",
        "deskripsi": "Tulang daun terlihat lebih tebal atau menonjol dibandingkan daun normal. Ciri khas infeksi virus yang menyebabkan deformasi daun."
    },
    {
        "kode": "G10",
        "nama": "Bakal buah atau bunga gugur",
        "deskripsi": "Calon buah atau bunga tidak berkembang dan gugur. Dapat disebabkan stres fisiologis atau infeksi patogen tertentu."
    },
    {
        "kode": "G11",
        "nama": "Tanaman kerdil",
        "deskripsi": "Pertumbuhan tanaman sangat terhambat sehingga ukuran keseluruhan lebih kecil dari normal. Biasanya akibat infeksi virus atau kerusakan akar."
    },
    {
        "kode": "G12",
        "nama": "Ditemukan kutu kebul (Bemisia tabaci)",
        "deskripsi": "Kehadiran hama kutu kebul pada daun bagian bawah. Pembawa utama virus kuning keriting pada cabai."
    }
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

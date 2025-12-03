from main import app
from models import db, Penyakit

# Data Penyakit & Solusi
DATA_PENYAKIT = [
    {
        "kode": "P1",
        "nama": "Rebah Semai",
        "deskripsi": "Penyakit yang menyerang bibit muda sehingga rebah mendadak. Disebabkan oleh jamur seperti Pythium, Rhizoctonia, atau Fusarium.",
        "solusi": "Gunakan media steril, hindari kelembapan berlebih, lakukan penyiraman dengan fungisida pada fase semai."
    },
    {
        "kode": "P2",
        "nama": "Layu Bakteri",
        "deskripsi": "Disebabkan oleh bakteri Ralstonia solanacearum. Tanaman tiba-tiba layu meski tanah basah. Akar dan batang bagian bawah menghitam.",
        "solusi": "Gunakan varietas tahan, rotasi tanaman, dan sanitasi lahan. Cabut tanaman yang terinfeksi."
    },
    {
        "kode": "P3",
        "nama": "Layu Fusarium",
        "deskripsi": "Disebabkan jamur Fusarium oxysporum. Daun menguning, tanaman layu perlahan, dan pembuluh batang berubah kecoklatan.",
        "solusi": "Gunakan fungisida sistemik, sterilisasi tanah, dan gunakan varietas tahan Fusarium."
    },
    {
        "kode": "P4",
        "nama": "Busuk Phythophtora",
        "deskripsi": "Disebabkan oleh jamur air Phytophthora capsici. Menyerang akar, batang, dan buah. Gejala berupa busuk basah meluas.",
        "solusi": "Perbaiki drainase, hindari genangan air, gunakan fungisida berbahan aktif metalaksil atau fosetil-Al."
    },
    {
        "kode": "P5",
        "nama": "Kuncup Daun",
        "deskripsi": "Daun tampak menggulung ke bawah, tebal, dan kaku. Biasanya disebabkan oleh virus atau hama penghisap seperti thrips.",
        "solusi": "Kendalikan vektor seperti thrips dan kutu kebul. Gunakan insektisida sistemik dan perangkap lengket."
    },
    {
        "kode": "P6",
        "nama": "Bercak Cercospora",
        "deskripsi": "Penyakit bercak daun akibat jamur Cercospora capsici. Bercak keabu-abuan, meluas, dan menyebabkan daun gugur.",
        "solusi": "Gunakan fungisida mankozeb/klorotalonil dan lakukan sanitasi daun terinfeksi."
    },
    {
        "kode": "P7",
        "nama": "Bercak Bakteri",
        "deskripsi": "Disebabkan bakteri Xanthomonas campestris. Bercak berwarna coklat gelap dengan tepi kuning pada daun.",
        "solusi": "Gunakan bakterisida berbahan kasugamisin atau tembaga. Jaga kebersihan lahan."
    },
    {
        "kode": "P8",
        "nama": "Antraknosa",
        "deskripsi": "Buah menunjukkan bercak cekung hitam dan busuk. Disebabkan jamur Colletotrichum capsici.",
        "solusi": "Buang buah terinfeksi, gunakan fungisida tembaga atau azoksistrobin."
    },
    {
        "kode": "P9",
        "nama": "Virus Gemini (Keriting Kuning)",
        "deskripsi": "Daun keriting, menebal, dan warna belang hijau-kuning. Disebabkan oleh Gemini virus yang dibawa kutu kebul (Bemisia tabaci).",
        "solusi": "Kendalikan kutu kebul dengan imidakloprid dan gunakan perangkap kuning."
    },
    {
        "kode": "P10",
        "nama": "Embun Tepung",
        "deskripsi": "Daun tertutup lapisan putih seperti bedak. Akibat serangan jamur Oidium sp. Menghambat fotosintesis.",
        "solusi": "Semprot fungisida sulfur, kurangi kelembapan, dan perbaiki sirkulasi udara."
    }
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

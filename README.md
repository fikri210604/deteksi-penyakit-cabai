Sistem Pakar Deteksi Penyakit Cabai (Fuzzy Sugeno)
==================================================

Proyek web berbasis Flask untuk mendiagnosa penyakit tanaman cabai menggunakan inferensi Fuzzy model Sugeno dengan Rule Group (multi‑gejala). Aplikasi menyediakan panel admin untuk mengelola basis pengetahuan (gejala, penyakit, dan kelompok aturan), serta panel pengguna untuk melakukan diagnosa dengan memilih gejala dan keterangannya.

Fitur
-----

- Admin
  - CRUD Gejala (kode otomatis `G{n}` bila dikosongkan)
  - CRUD Penyakit (kode otomatis `P{n}` bila dikosongkan)
  - CRUD Kelompok Rule (Rule Group) multi‑gejala
    - Tambah beberapa kondisi: (Gejala + Term) dengan term: `tidak_ada, sedikit, sedang, banyak, sangat_banyak`
    - Pilih penyakit hasil, konsekuen Sugeno (`rendah/sedang/tinggi`)
    - Bobot rule (`0..1`), status aktif/nonaktif
    - z override opsional (`0..1`) untuk mengganti nilai default Sugeno per group
    - Keterangan opsional untuk dokumentasi aturan
  - Lihat data user
- Pengguna
  - Input diagnosa via form “Gejala + Keterangan” (dapat menambah beberapa baris)
  - Lihat hasil diagnosa (penyakit teratas + nilai keyakinan)
  - Lihat riwayat diagnosa

Arsitektur Singkat
------------------

- Framework: Flask + Jinja2
- ORM: SQLAlchemy (Flask‑SQLAlchemy)
- Autentikasi: Flask‑Login
- DB: MySQL/MariaDB (driver PyMySQL)
- Konfigurasi: `.env` (python‑dotenv)
- Inferensi: Fuzzy Sugeno (Rule Group, multi‑gejala)

Struktur Direktori (ringkas)
----------------------------

- `main.py` — entry Flask, registrasi blueprint
- `models.py` — model SQLAlchemy: `User, Gejala, Penyakit, RuleGroup, RuleCondition, History`
- `controllers/` — route admin & user (blueprint): auth, user, diagnosis, admin/*
- `templates/` — Jinja template (sidebar untuk halaman dalam, navbar untuk landing)
- `database/` — seeder
  - `database/database_seeder.py` — jalankan semua seeder
  - `database/seeders/*.py` — data awal gejala, penyakit, admin/user, rule group
- `fuzzy_logic.py` — mesin Fuzzy Sugeno + fuzzifikasi

Persiapan
---------

1) Buat environment `.env` di root:

```
SECRET_KEY=your-secret
DB_USER=root
DB_PASSWORD=your-password
DB_HOST=127.0.0.1
DB_PORT=3306
DB_NAME=sistem_pakar_cabai
```

2) Instal dependensi (contoh):

```
pip install Flask Flask-Login Flask-SQLAlchemy PyMySQL python-dotenv
```

3) Siapkan database MySQL kosong dengan nama sesuai `DB_NAME`.

Menjalankan Aplikasi
--------------------

- Jalankan seeder (membuat tabel + isi data awal):

```
python -m database.database_seeder
```

- Jalankan aplikasi:

```
python main.py
```

- Akses di browser: `http://localhost:5000`

Kredensial Awal
---------------

- Admin: `admin` / `admin123`
- Beberapa user dummy juga di‑seed

Cara Pakai
----------

- Pengguna
  - Login → pilih “Input Gejala”
  - Tambah baris “Gejala + Keterangan” sesuai kondisi tanaman
  - Klik “Proses Diagnosa” → hasil penyakit + skor
  - Lihat riwayat di menu “Riwayat”

- Admin
  - Login admin → tampil sidebar admin
  - Kelola Gejala/Penyakit (CRUD; kode otomatis jika dikosongkan)
  - Kelola Rule
    - Masuk menu “Kelompok Rule” → “Tambah Kelompok”
    - Tambah beberapa kondisi: (Gejala + Term)
    - Pilih penyakit target, konsekuen Sugeno (rendah/sedang/tinggi)
    - Opsional: isi `z override` (0..1) untuk mengganti nilai z default map
    - Simpan; aturan aktif langsung dipakai dalam inferensi

Mekanisme Fuzzy (Sugeno)
------------------------

- Domain input: 0..1
- Fuzzifikasi term antecedent (default global, dapat dituning di kode):
  - `tidak_ada`: trap(0.0, 0.0, 0.05, 0.2)
  - `sedikit`: tri(0.1, 0.25, 0.4)
  - `sedang`: tri(0.3, 0.5, 0.7)
  - `banyak`: tri(0.6, 0.75, 0.9)
  - `sangat_banyak`: trap(0.8, 0.95, 1.0, 1.0)
- Inferensi per Rule Group:
  - α = min(µ(kondisi‑kondisi yang diisi pengguna))
  - z (Sugeno):
    - Default map: `rendah=0.2`, `sedang=0.5`, `tinggi=0.8`
    - Jika `z_override` diisi pada group, maka pakai nilai tersebut
  - Bobot group (0..1) mengalikan α (opsional)
- Agregasi per penyakit: `score_penyakit = Σ(α · z) / Σα`
- Pemilihan hasil: penyakit dengan skor tertinggi

Catatan: Kondisi (gejala) yang tidak diisi pengguna diabaikan (netral). Jika tidak ada satu pun kondisi yang match, hasil bisa “Tidak diketahui”.

Troubleshooting
--------------

- “Unknown column …” setelah mengubah model
  - SQLAlchemy `create_all()` tidak ALTER tabel. Jika skema berubah, lakukan migrasi:
    - Opsi cepat dev: drop tabel terkait lalu jalankan `create_all()` (via seeder)
    - Opsi proper: gunakan Alembic/Flask‑Migrate
- Hasil diagnosa 0 / “Tidak diketahui”
  - Pastikan ada Rule Group aktif dengan kondisi tersimpan
  - Pastikan input pengguna cocok dengan term di Rule Group
  - Coba skenario uji: pilih gejala yang memang menjadi kondisi di salah satu Rule Group
- Rule sederhana (single gejala) tidak dipakai
  - Sistem kini hanya memakai Rule Group (Sugeno)

Poin Pengembangan Lanjut
------------------------

- Tuning kurva fuzzifikasi per gejala (bukan global)
- Editor parameter kurva di admin (geser titik tri/trap)
- Tampilan transparansi hasil (α dan z per group pada halaman hasil)
- Alembic/Flask‑Migrate untuk migrasi skema versi produksi

Lisensi
-------

Tidak ditentukan. Tambahkan lisensi sesuai kebutuhan proyek Anda.


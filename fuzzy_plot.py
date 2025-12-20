import numpy as np
import matplotlib.pyplot as plt

"""
Plot util untuk visualisasi fuzzy yang konsisten dengan engine di fuzzy_logic.py

Fitur:
- Plot fungsi keanggotaan (domain 0..1 dan opsi tampilan 0..100)
- Plot bobot seluruh gejala (BOBOT_GEJALA)
- Plot bobot seluruh penyakit (BOBOT_PENYAKIT)

Catatan:
- Di engine, term "tidak" diset 0 (tidak digunakan); maka tidak diplot sebagai kurva aktif.
"""

# Nilai ambang untuk menampilkan angka. Nilai <= EPS tidak akan diberi angka.
EPS = 1e-6


def segitiga(x, a, b, c):
    mu = np.zeros_like(x, dtype=float)
    # naik
    idx = (x > a) & (x < b)
    mu[idx] = (x[idx] - a) / (b - a)
    # turun
    idx = (x >= b) & (x < c)
    mu[idx] = (c - x[idx]) / (c - b)
    return np.clip(mu, 0.0, 1.0)


def trapesium(x, a, b, c, d):
    mu = np.zeros_like(x, dtype=float)
    # area datar
    idx_flat = (x >= b) & (x <= c)
    mu[idx_flat] = 1.0
    # naik
    if b > a:
        idx = (x > a) & (x < b)
        mu[idx] = (x[idx] - a) / (b - a)
    # turun
    if d > c:
        idx = (x > c) & (x < d)
        mu[idx] = (d - x[idx]) / (d - c)
    return np.clip(mu, 0.0, 1.0)


def plot_fuzzifikasi(domain_mode="0-100"):
    if domain_mode == "0-100":
        x = np.linspace(0, 100, 500)
        x01 = x / 100.0
        x_label = "Nilai Gejala"
        fname = "grafik_fuzzifikasi_gejala_jurnal.png"
        xticks = [0, 30, 45, 60, 100]
    else:
        x01 = np.linspace(0.0, 1.0, 500)
        x = x01
        x_label = "Ditemukan kutu kebul"
        fname = "grafik_fuzzifikasi_gejala.png"
        xticks = [0.0, 0.3, 0.45, 0.6, 1.0]

    # Konsisten dengan engine
    mu_sedikit = trapesium(x01, 0.0, 0.0, 0.3, 0.45)
    mu_sedang  = segitiga(x01, 0.3, 0.45, 0.6)
    mu_banyak  = trapesium(x01, 0.45, 0.6, 1.0, 1.0)

    plt.figure(figsize=(7, 3.5))

    plt.plot(x, mu_sedikit, label="Sedikit", linewidth=2, color="green")
    plt.plot(x, mu_sedang,  label="Sedang",  linewidth=2, color="blue")
    plt.plot(x, mu_banyak,  label="Banyak",  linewidth=2, color="red")

    plt.xlabel(x_label)
    plt.ylabel("μ(x)")
    plt.ylim(0, 1.05)

    # INI BAGIAN PALING PENTING
    plt.xticks(xticks)
    plt.yticks([0, 0.5, 1])

    plt.grid(axis="y", linestyle=":", alpha=0.4)
    plt.legend(frameon=False)
    plt.tight_layout()
    plt.savefig(fname, dpi=300)
    plt.close()

    return fname



# Bobot dari engine
try:
    from fuzzy_logic import BOBOT_GEJALA, BOBOT_PENYAKIT
except Exception:
    BOBOT_GEJALA, BOBOT_PENYAKIT = {}, {}


def plot_bobot_gejala():
    if not BOBOT_GEJALA:
        return None
    items = sorted(BOBOT_GEJALA.items(), key=lambda kv: kv[0])
    labels = [k for k, _ in items]
    values = [v for _, v in items]
    plt.figure(figsize=(max(8, len(labels) * 0.6), 4))
    bars = plt.bar(labels, values, color="#3b82f6")
    plt.ylim(0, 1.05)
    plt.ylabel("Bobot")
    plt.title("Bobot Gejala (0..1)")
    plt.grid(axis="y", linestyle=":", alpha=0.4)
    for b, v in zip(bars, values):
        if v > EPS:
            plt.text(b.get_x() + b.get_width()/2.0, v + 0.02, f"{v:.2f}", ha="center", va="bottom", fontsize=8)
    plt.tight_layout()
    fname = "grafik_bobot_gejala.png"
    plt.savefig(fname, dpi=300)
    plt.close()
    return fname


def plot_bobot_penyakit():
    if not BOBOT_PENYAKIT:
        return None
    items = sorted(BOBOT_PENYAKIT.items(), key=lambda kv: kv[0])
    labels = [k for k, _ in items]
    values = [v for _, v in items]
    plt.figure(figsize=(max(8, len(labels) * 0.6), 4))
    bars = plt.bar(labels, values, color="#22c55e")
    plt.ylim(0, 1.05)
    plt.ylabel("Bobot")
    plt.title("Bobot Penyakit (0..1)")
    plt.grid(axis="y", linestyle=":", alpha=0.4)
    for b, v in zip(bars, values):
        if v > EPS:
            plt.text(b.get_x() + b.get_width()/2.0, v + 0.02, f"{v:.2f}", ha="center", va="bottom", fontsize=8)
    plt.tight_layout()
    fname = "grafik_bobot_penyakit.png"
    plt.savefig(fname, dpi=300)
    plt.close()
    return fname


def _normalize_status(status):
    if isinstance(status, str):
        s = status.strip().lower()
        if s in {"ya", "y", "true", "1"}:
            return True
        if s in {"tidak", "t", "false", "0", "no", "n"}:
            return False
    return bool(status)


def plot_penyakit_biner(label="Penyakit", status="ya", fname=None):
    """
    Plot keputusan biner penyakit: Ya=1, Tidak=0.

    Args:
        label: Nama/teks penyakit untuk judul.
        status: 'ya' | 'tidak' | bool | 0/1.
        fname: Nama file output (opsional).

    Returns:
        Path file gambar yang disimpan.
    """
    is_yes = _normalize_status(status)

    labels = ["Tidak", "Ya"]
    values = [1, 0] if not is_yes else [0, 1]

    plt.figure(figsize=(4.5, 3.2))
    colors = ["#ef4444", "#22c55e"]  # merah untuk tidak, hijau untuk ya
    bars = plt.bar(labels, values, color=colors)

    plt.ylim(0, 1.05)
    plt.ylabel("Keputusan (0/1)")
    title_suffix = "Ya" if is_yes else "Tidak"
    plt.title(f"{label}: {title_suffix}")
    plt.grid(axis="y", linestyle=":", alpha=0.4)

    for b, v in zip(bars, values):
        plt.text(b.get_x() + b.get_width() / 2.0, v + 0.03, f"{int(v)}", ha="center", va="bottom", fontsize=9)

    plt.tight_layout()
    if not fname:
        safe_label = str(label).strip().lower().replace(" ", "_") or "penyakit"
        fname = f"grafik_{safe_label}_ya_tidak.png"
    plt.savefig(fname, dpi=300)
    plt.close()
    return fname

def plot_hasil_fuzzy(label, nilai, fname=None):
    """
    Plot hasil skor fuzzy (0.0 sampai 1.0) dalam bentuk bar meter.
    
    Args:
        label: Nama penyakit (misal: "Bercak Daun")
        nilai: Float 0.0 s.d 1.0 (misal: 0.75)
    """
    plt.figure(figsize=(6, 2))
    
    # 1. Background bar (abu-abu full 0-1)
    plt.barh([0], [1.0], color="#e5e7eb", height=0.5, edgecolor='black')
    
    # 2. Tentukan warna berdasarkan nilai (Merah -> Kuning -> Hijau)
    if nilai < 0.4:
        color = "#ef4444" # Merah (Rendah)
    elif nilai < 0.7:
        color = "#eab308" # Kuning (Sedang)
    else:
        color = "#22c55e" # Hijau (Tinggi/Yakin)
        
    # 3. Value bar (bar yang terisi sesuai nilai)
    plt.barh([0], [nilai], color=color, height=0.5, edgecolor='black')
    
    # Kosmetik Grafik
    plt.xlim(0, 1.0)
    plt.ylim(-0.5, 0.5)
    plt.yticks([]) # Hilangkan sumbu Y
    plt.xticks([0.0, 0.25, 0.5, 0.75, 1.0])
    plt.xlabel("Tingkat Keyakinan (μ)")
    plt.title(f"Hasil Diagnosa: {label}")
    
    # Tambahkan teks angka di tengah/ujung bar
    plt.text(nilai if nilai > 0.1 else 0.1, 0, f"{nilai*100:.1f}%", 
             ha='center', va='center', color='white' if nilai > 0.5 else 'black', 
             fontweight='bold')

    plt.tight_layout()
    
    if not fname:
        safe_label = str(label).strip().lower().replace(" ", "_")
        fname = f"grafik_hasil_{safe_label}.png"
        
    plt.savefig(fname, dpi=300)
    plt.close()
    return fname
def plot_posisi_penyakit(label, nilai, fname=None):
    """
    Memvisualisasikan hasil diagnosa dalam bentuk kurva fuzzy (Output Membership).
    Menunjukkan posisi nilai hasil (0.0 - 1.0) terhadap himpunan fuzzy.
    """
    # Domain 0 sampai 1
    x = np.linspace(0, 1.0, 500)
    
    # Definisi Himpunan Fuzzy untuk Output (Keputusan)
    # Sesuaikan batas ini dengan logika engine Anda jika perlu.
    # Di sini saya pakai standar umum:
    # - Rendah/Tidak: 0.0 - 0.4
    # - Sedang/Ragu : 0.3 - 0.7
    # - Tinggi/Ya   : 0.6 - 1.0
    mu_rendah = trapesium(x, -0.1, 0.0, 0.3, 0.45) # Kurva Hijau (Kecil Kemungkinan)
    mu_sedang = segitiga(x, 0.3, 0.5, 0.7)         # Kurva Biru (Sedang/Ragu)
    mu_tinggi = trapesium(x, 0.55, 0.7, 1.0, 1.1)  # Kurva Merah (Tinggi Kemungkinan)

    plt.figure(figsize=(7, 3.5))

    # 1. Plot Kurva Himpunan
    plt.plot(x, mu_rendah, label="Kecil", color="green", linewidth=1.5, alpha=0.6)
    plt.fill_between(x, mu_rendah, alpha=0.1, color="green")
    
    plt.plot(x, mu_sedang, label="Sedang", color="blue", linewidth=1.5, alpha=0.6)
    plt.fill_between(x, mu_sedang, alpha=0.1, color="blue")
    
    plt.plot(x, mu_tinggi, label="Tinggi", color="red", linewidth=1.5, alpha=0.6)
    plt.fill_between(x, mu_tinggi, alpha=0.1, color="red")

    # 2. Plot Garis Hasil (Indikator Nilai Akhir)
    # Ini garis tegak lurus yang menunjukkan hasil diagnosa Anda ada di mana
    plt.axvline(x=nilai, color='black', linestyle='--', linewidth=2, label=f"Hasil: {nilai:.2f}")

    # Kosmetik
    plt.title(f"Visualisasi Output Fuzzy: {label}")
    plt.xlabel("Tingkat Keyakinan (0-1)")
    plt.ylabel("μ(x)")
    plt.ylim(0, 1.1)
    plt.xlim(0, 1.0)
    plt.yticks([0, 0.5, 1])
    plt.grid(axis="y", linestyle=":", alpha=0.4)
    plt.legend(loc='upper left', frameon=True, fontsize='small')
    plt.tight_layout()

    if not fname:
        safe_label = str(label).strip().lower().replace(" ", "_")
        fname = f"grafik_posisi_{safe_label}.png"

    plt.savefig(fname, dpi=300)
    plt.close()
    return fname
    
if __name__ == "__main__":
    # 1) Plot fungsi keanggotaan
    print("Menyimpan:", plot_fuzzifikasi("0-1"))
    print("Menyimpan:", plot_fuzzifikasi("0-100"))

    # 2) Plot bobot
    fg = plot_bobot_gejala()
    if fg:
        print("Menyimpan:", fg)
    fp = plot_bobot_penyakit()
    if fp:
        print("Menyimpan:", fp)

    # --- TAMBAHAN BARU DI SINI ---
    # 3) Plot Penyakit Biner (Contoh Penggunaan)


    print("Menyimpan:", plot_hasil_fuzzy(label="Penyakit Bercak Daun", nilai=0.85))
    
    # Contoh untuk penyakit lain yang nilainya kecil
    print("Menyimpan:", plot_hasil_fuzzy(label="Penyakit Busuk Batang", nilai=0.25))

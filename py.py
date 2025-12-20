import numpy as np
import matplotlib.pyplot as plt

def plot_output_penyakit_custom(label="Virus Gemini", fname=None):
    """
    Membuat plot output penyakit sesuai referensi:
    - Domain x: 0 s.d 100
    - Area Transisi (Fuzzy): 0 s.d 10
    - Area Tegas (Yakin): 10 s.d 100
    """
    # 1. Setup Data (Domain 0 - 100)
    x = np.linspace(0, 100, 500)

    # 2. Rumus Logika Kurva
    # Kurva "Tidak" (Hijau): Turun dari 1 ke 0 pada range 0-10
    mu_tidak = np.clip((10 - x) / 10.0, 0.0, 1.0)

    # Kurva "Ya" (Biru): Naik dari 0 ke 1 pada range 0-10
    mu_ya = np.clip(x / 10.0, 0.0, 1.0)

    # 3. Setup Plotting
    plt.figure(figsize=(7, 3.5))

    # Plot Garis dengan ketebalan dan warna khusus
    plt.plot(x, mu_tidak, label="Tidak", color="#8CB369", linewidth=4) # Hijau Pupus
    plt.plot(x, mu_ya,    label="Ya",    color="#4575B4", linewidth=4) # Biru Laut

    # 4. Kosmetik Grafik (Styling)
    plt.title(label, fontsize=14, fontweight='bold', color='#333333', pad=15)
    
    # Grid hanya horizontal (axis='y') agar bersih
    plt.grid(axis='y', linestyle='-', alpha=0.3, color='gray')
    
    # Batas Axis
    plt.xlim(0, 100)
    plt.ylim(0, 1.05)

    # Ticks (Angka di sumbu)
    # Sumbu X: Hanya menampilkan angka penting: 0, 10, dan 100
    plt.xticks([0, 10, 100], fontsize=11)
    # Sumbu Y: Standar 0 sampai 1
    plt.yticks([0, 0.2, 0.4, 0.6, 0.8, 1.0], fontsize=10)

    # Legenda (Keterangan warna)
    plt.legend(loc='center right', frameon=False, fontsize=11)

    plt.tight_layout()

    # 5. Simpan File
    if not fname:
        # Membersihkan nama file dari spasi
        safe_label = str(label).strip().lower().replace(" ", "_")
        fname = f"grafik_output_{safe_label}.png"

    plt.savefig(fname, dpi=300)
    plt.close()
    
    return fname

# --- Bagian Eksekusi ---
if __name__ == "__main__":
    # Contoh 1: Virus Gemini
    file1 = plot_output_penyakit_custom(label="Virus Gemini")
    print(f"Grafik berhasil disimpan: {file1}")

    # Contoh 2: Penyakit Lain
    file2 = plot_output_penyakit_custom(label="Penyakit Busuk Batang")
    print(f"Grafik berhasil disimpan: {file2}")
import os
import sys

# Pastikan root project ada di sys.path agar import main/models terbaca
CURRENT_DIR = os.path.dirname(__file__)
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from database.seeders.gejala_seeder import run_gejala_seeder
from database.seeders.penyakit_seeder import run_penyakit_seeder
from database.seeders.admin_seeder import run_admin_seeder
from database.seeders.user_seeder import run_user_seeder
from database.seeders.rule_group_seeder import run_rule_group_seeder
from main import app, db

if __name__ == "__main__":
    print("=======================================")
    print("   MENJALANKAN SEMUA SEEDER OTOMATIS   ")
    print("=======================================\n")
    
    with app.app_context():
        db.create_all()
        print("[INFO] Struktur database dipastikan ada.\n")
    
        run_gejala_seeder()
        run_penyakit_seeder()
        run_rule_group_seeder()
        run_admin_seeder()
        run_user_seeder()

    print("\n=======================================")
    print("   SEMUA DATA BERHASIL DI-GENERATE!    ")
    print("=======================================")

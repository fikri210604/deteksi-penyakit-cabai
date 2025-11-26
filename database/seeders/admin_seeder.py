from main import app
from models import db, User
from werkzeug.security import generate_password_hash

def run_admin_seeder():
    with app.app_context():
        print("--- Memulai Seeding Admin ---")
        
        admin_username = "admin"
        admin_email = "admin@example.com"
        admin_pass = "admin123"

        # Cek apakah admin sudah ada
        exists = User.query.filter_by(username=admin_username).first()
        
        if not exists:
            hashed_pw = generate_password_hash(admin_pass, method='pbkdf2:sha256')
            
            new_admin = User(
                username=admin_username,
                email=admin_email,
                password=hashed_pw,
                role='admin' 
            )
            db.session.add(new_admin)
            db.session.commit()
            print(f"[+] Admin dibuat: User={admin_username}, Pass={admin_pass}")
        else:
            print("[-] Akun Admin sudah ada, tidak perlu dibuat ulang.")
        
        print("--- Selesai Seeding Admin ---\n")

if __name__ == "__main__":
    run_admin_seeder()

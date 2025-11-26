from main import app
from models import db, User
from werkzeug.security import generate_password_hash

def run_user_seeder():
    with app.app_context():
        print("--- Memulai Seeding User Dummy ---")
        
        users = [
            {"u": "petani1", "e": "petani1@test.com", "p": "123456"},
            {"u": "budi_tani", "e": "budi@test.com", "p": "123456"},
        ]

        count = 0
        for u in users:
            exists = User.query.filter_by(username=u['u']).first()
            if not exists:
                hashed_pw = generate_password_hash(u['p'], method='pbkdf2:sha256')
                new_user = User(
                    username=u['u'],
                    email=u['e'],
                    password=hashed_pw,
                    role='user'
                )
                db.session.add(new_user)
                count += 1
                print(f"[+] User dibuat: {u['u']}")
            else:
                print(f"[-] User {u['u']} sudah ada.")

        db.session.commit()
        print(f"--- Selesai! {count} user dummy ditambahkan. ---\n")

if __name__ == "__main__":
    run_user_seeder()

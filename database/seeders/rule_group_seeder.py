from main import app
from models import db, RuleGroup, RuleCondition, Penyakit, Gejala


def run_rule_group_seeder():
    with app.app_context():
        print("--- Memulai Seeding Rule Group (Tsukamoto) ---")

        DATA_RULES = [
            # P1 – ANTRAKNOSA (6 RULE)
            {
                "nama": "RG-P1-1",
                "kode_penyakit": "P1",
                "kondisi": [("G1","B"), ("G7","S"), ("G8","D")]
            },
            {
                "nama": "RG-P1-2",
                "kode_penyakit": "P1",
                "kondisi": [("G1","B"), ("G7","D"), ("G8","D")]
            },
            {
                "nama": "RG-P1-3",
                "kode_penyakit": "P1",
                "kondisi": [("G1","B"), ("G7","B"), ("G8","D")]
            },
            {
                "nama": "RG-P1-4",
                "kode_penyakit": "P1",
                "kondisi": [("G1","B"), ("G7","S"), ("G8","B")]
            },
            {
                "nama": "RG-P1-5",
                "kode_penyakit": "P1",
                "kondisi": [("G1","B"), ("G7","D"), ("G8","B")]
            },
            {
                "nama": "RG-P1-6",
                "kode_penyakit": "P1",
                "kondisi": [("G1","B"), ("G7","B"), ("G8","B")]
            },
                # =========================
                # P2 – CERCOSPORA (6 RULE)
                # =========================
            {
                "nama": "RG-P2-1",
                "kode_penyakit": "P2",
                "kondisi": [("G1","S"), ("G2","D"), ("G3","S"), ("G8","B")]
            },
            {
                "nama": "RG-P2-2",
                "kode_penyakit": "P2",
                "kondisi": [("G1","D"), ("G2","B"), ("G3","S"), ("G8","B")]
            },
            {
                "nama": "RG-P2-3",
                "kode_penyakit": "P2",
                "kondisi": [("G1","B"), ("G2","D"), ("G3","D"), ("G8","B")]
            },
            {
                "nama": "RG-P2-4",
                "kode_penyakit": "P2",
                "kondisi": [("G1","S"), ("G2","B"), ("G3","D"), ("G8","B")]
            },
            {
                "nama": "RG-P2-5",
                "kode_penyakit": "P2",
                "kondisi": [("G1","D"), ("G2","D"), ("G3","B"), ("G8","B")]
            },
            {
                "nama": "RG-P2-6",
                "kode_penyakit": "P2",
                "kondisi": [("G1","B"), ("G2","B"), ("G3","B"), ("G8","B")]
            },
                # =========================
                # P3 – VIRUS GEMINI (6 RULE)
                # =========================
            {
                "nama": "RG-P3-1",
                "kode_penyakit": "P3",
                "kondisi": [("G4","B"), ("G5","S"), ("G9","S"), ("G11","B"), ("G12","D")]
            },
            {
                "nama": "RG-P3-2",
                "kode_penyakit": "P3",
                "kondisi": [("G4","B"), ("G5","D"), ("G9","S"), ("G11","B"), ("G12","B")]
            },
            {
                "nama": "RG-P3-3",
                "kode_penyakit": "P3",
                "kondisi": [("G4","B"), ("G5","B"), ("G9","D"), ("G11","B"), ("G12","D")]
            },
            {
                "nama": "RG-P3-4",
                "kode_penyakit": "P3",
                "kondisi": [("G4","B"), ("G5","S"), ("G9","D"), ("G11","B"), ("G12","B")]
            },
            {
                "nama": "RG-P3-5",
                "kode_penyakit": "P3",
                "kondisi": [("G4","B"), ("G5","D"), ("G9","B"), ("G11","B"), ("G12","D")]
            },
            {
                "nama": "RG-P3-6",
                "kode_penyakit": "P3",
                "kondisi": [("G4","B"), ("G5","B"), ("G9","B"), ("G11","B"), ("G12","B")]
            },
                # =========================
                # P4 – KERUPUK (6 RULE)
                # =========================
            {
                "nama": "RG-P4-1",
                "kode_penyakit": "P4",
                "kondisi": [("G4","S"), ("G6","B"), ("G8","D"), ("G10","D"), ("G11","S")]
            },
            {
                "nama": "RG-P4-2",
                "kode_penyakit": "P4",
                "kondisi": [("G4","D"), ("G6","B"), ("G8","D"), ("G10","B"), ("G11","S")]
            },
            {
                "nama": "RG-P4-3",
                "kode_penyakit": "P4",
                "kondisi": [("G4","B"), ("G6","B"), ("G8","D"), ("G10","D"), ("G11","D")]
            },
            {
                "nama": "RG-P4-4",
                "kode_penyakit": "P4",
                "kondisi": [("G4","S"), ("G6","B"), ("G8","B"), ("G10","B"), ("G11","D")]
            },
            {
                "nama": "RG-P4-5",
                "kode_penyakit": "P4",
                "kondisi": [("G4","D"), ("G6","B"), ("G8","B"), ("G10","D"), ("G11","B")]
            },
            {
                "nama": "RG-P4-6",
                "kode_penyakit": "P4",
                "kondisi": [("G4","B"), ("G6","B"), ("G8","B"), ("G10","B"), ("G11","B")]
            },

        ]

        created = 0

        for ex in DATA_RULES:

            p = Penyakit.query.filter_by(kode_penyakit=ex["kode_penyakit"]).first()
            if not p:
                print(f"[SKIP] Penyakit {ex['kode_penyakit']} belum ada.")
                continue

            exists = RuleGroup.query.filter_by(nama=ex["nama"]).first()
            if exists:
                print(f"[-] Group {ex['nama']} sudah ada, skip.")
                continue

            grp = RuleGroup(
                nama=ex["nama"],
                kode_penyakit=ex["kode_penyakit"],
                aktif=True
            )
            db.session.add(grp)
            db.session.flush()  

            for kode_gjl, term in ex["kondisi"]:
                db.session.add(
                    RuleCondition(group_id=grp.id,
                                  kode_gejala=kode_gjl,
                                  antecedent_term=term)
                )

            db.session.commit()
            created += 1
            print(f"[OK] RuleGroup {ex['nama']} dibuat.")

        print(f"\nTOTAL CREATED: {created}")



if __name__ == '__main__':
    with app.app_context():
        run_rule_group_seeder()


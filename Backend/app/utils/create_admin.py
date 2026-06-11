from app.database import SessionLocal
from app.models.admin import Admin
from app.utils.security import hash_password


def main():
    db = SessionLocal()

    try:
        admin_email = "admin@aidg.lk"
        admin_password = "Admin12345"

        admin = db.query(Admin).filter(Admin.email == admin_email).first()

        if admin:
            admin.name = "System Admin"
            admin.password_hash = hash_password(admin_password)
            admin.is_active = True
            print("Existing admin password reset successfully.")
        else:
            admin = Admin(
                name="System Admin",
                email=admin_email,
                password_hash=hash_password(admin_password),
                is_active=True
            )
            db.add(admin)
            print("New admin created successfully.")

        db.commit()

        print("Admin email:", admin_email)
        print("Admin password:", admin_password)

    except Exception as error:
        db.rollback()
        print("Admin creation failed.")
        print(error)

    finally:
        db.close()


if __name__ == "__main__":
    main()
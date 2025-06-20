

from app.models.user import User, Role
from app.core.security import hash_password
from sqlmodel import Session, select
from app.db.session import engine

def create_admin_user():
    with Session(engine) as session:
        existing = session.exec(
            select(User).where(User.email == "precious@example.com")
        ).first()
        if not existing:
            admin_user = User(
                email="precious@example.com",
                hashed_password=hash_password("precious42idam"),
                role=Role.ADMIN,
                is_active=True,
                is_verified=True,
                fullname="Precious Idam",
                phone="08162300796",
            )
            session.add(admin_user)
            session.commit()
            session.refresh(admin_user)
            print("Admin user created:", admin_user.email)
        else:
            print("Admin user already exists:", existing.email)

if __name__ == "__main__":
    create_admin_user()
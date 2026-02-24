import logging
from app.db.database import SessionLocal
from app.models.user import User, RoleEnum
from app.core.security import get_password_hash

logger = logging.getLogger(__name__)

def init_admin_user():
    db = SessionLocal()
    try:
        admin = db.query(User).filter(User.username == "admin").first()
        if not admin:
            logger.info("Admin user not found. Creating default admin...")
            admin_user = User(
                username="admin",
                email="admin@example.com",
                hashed_password=get_password_hash("admin"),
                role=RoleEnum.ADMIN
            )
            db.add(admin_user)
            db.commit()
            logger.info("Admin user created successfully! (login: admin, password: admin)")
        else:
            logger.info("Admin user already exists. Skipping creation.")
    except Exception as e:
        logger.error(f"Error during DB initialization: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_admin_user()
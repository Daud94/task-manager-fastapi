from sqlalchemy.orm import Session

from db.models import User
from db.schemas.user_schema import UserBaseInput


def get_user_by_email(db: Session, email: str):
    user = db.query(User).filter(email == User.email).first()
    return user


def get_user_by_id(db: Session, id: int):
    user = db.query(User).filter(id == User.id).first()
    return user


def get_all_users(db: Session):
    return db.query(User).all()


# from passlib.context import CryptContext
# password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
import passlib.hash as password_hash


class Hash():
    def hash(password: str) -> str:
        return password_hash.bcrypt.hash(password)

    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return password_hash.bcrypt.verify(plain_password, hashed_password)
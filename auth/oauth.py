import os
from datetime import timedelta, datetime, timezone
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt import InvalidTokenError
from sqlalchemy.orm import Session
from dotenv import load_dotenv

from db.schemas.user_schema import UserBaseInput, UserBaseOut
from services import user_service

from dotenv import load_dotenv

load_dotenv()
secret_key = os.getenv("SECRET_KEY")
algorithm  = os.getenv("ALGORITHM")
token_expiration = os.getenv("TOKEN_EXPIRATION")

from db.database import get_db

oauth2_schema = OAuth2PasswordBearer(tokenUrl='auth/token')


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(hours=1)

    to_encode.update({'exp': expire})
    token = jwt.encode(to_encode, secret_key, algorithm=algorithm)
    return token

def get_current_user(token: Annotated[str, Depends(oauth2_schema)], db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate': 'Bearer'}
    )
    try:
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        user_id = payload.get('user_id')
        user = user_service.get_user_by_id(db, user_id)
        if not user:
            raise credentials_exception
        return UserBaseInput.model_validate(user, from_attributes=True)
    except InvalidTokenError:
        raise credentials_exception

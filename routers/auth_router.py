import logging
import os
from datetime import timedelta, datetime, timezone

import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from db.database import get_db
from db.models import User
from db.schemas.user_schema import CreateUser
from services.user_service import get_user_by_email
from utils.hash import Hash
from dotenv import load_dotenv

load_dotenv()
secret_key = os.getenv("SECRET_KEY")
algorithm  = os.getenv("ALGORITHM")
token_expiration = os.getenv("TOKEN_EXPIRATION")



logger = logging.getLogger(__name__)

router = APIRouter(prefix='/auth', tags=['authentication'])


@router.post('/signup')
def signup(request: CreateUser, db: Session = Depends(get_db)):
    try:
        existing_user = get_user_by_email(db, request.email)
        if existing_user:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Email already registered')

        user = User(
            first_name=request.first_name,
            last_name=request.last_name,
            email=request.email,
            phone_number=request.phone_number,
            password=Hash.bcrypt(request.password),
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        return JSONResponse(content={
            'success': True,
            'message': 'User created successfully',
        }, status_code=200, media_type='application/json')
    except Exception as err:
        db.rollback()
        logger.error(err)
        return JSONResponse(content={
            'success': False,
            'message': err.detail,
        }, status_code=err.status_code, media_type='application/json')
        # raise HTTPException(status_code=err.status_code, detail=err.detail)
    finally:
        db.close()


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(hours=1)

    to_encode.update({'exp': expire})
    token = jwt.encode(to_encode, secret_key, algorithms=algorithm)
    return token


@router.post('/token')
def login(request: OAuth2PasswordRequestForm, db: Session = Depends(get_db)):
    existing_user: User | None = db.query(User).filter(request.username == User.email).first()
    if not existing_user:
        raise HTTPException(status_code=404, detail='User not found')

    is_match = Hash.verify_password(request.password, existing_user.password)
    if not is_match:
        raise HTTPException(status_code=401, detail='Incorrect password')
    
    access_token = create_access_token(data={'user': existing_user.email}, expires_delta=timedelta(hours=1))
    return {
        'access_token': access_token,
        'token_type': 'Bearer',
        'user_id': existing_user.id,
        'username': existing_user.email
    }

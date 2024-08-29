import logging
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from auth.oauth import create_access_token
from db.database import get_db
from db.models import User
from db.schemas.user_schema import CreateUser
from services.user_service import get_user_by_email
from utils.hash import Hash




logger = logging.getLogger(__name__)

router = APIRouter(prefix='/auth', tags=['Authentication'])


@router.post('/signup', status_code=status.HTTP_201_CREATED)
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
            password=Hash.hash(request.password),
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        return {
            'message': True,
            'success': "Signup successful",
        }
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

@router.post('/token')
def login(request: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    existing_user= db.query(User).filter(request.username == User.email).first()
    if not existing_user:
        raise HTTPException(status_code=404, detail='User not found')
    print(existing_user.id)
    is_match = Hash.verify_password(request.password, existing_user.password)
    if not is_match:
        raise HTTPException(status_code=401, detail='Incorrect password')
    
    access_token = create_access_token(data={'user_id': existing_user.id}, expires_delta=timedelta(hours=1))
    return {
        'access_token': access_token,
        'token_type': 'Bearer',
        'user_id': existing_user.id,
        'username': existing_user.email
    }

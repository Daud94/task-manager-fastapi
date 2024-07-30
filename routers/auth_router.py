import logging

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from starlette.responses import Response, JSONResponse

from db.database import get_db
from db.models import User
from db.schemas.user_schema import CreateUser
from services.user_service import get_user_by_email
from utils.hash import Hash

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

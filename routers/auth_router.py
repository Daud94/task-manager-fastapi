from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from db.database import get_db
from db.models import User
from db.schemas.user_schema import CreateUser
from services.user_service import get_user_by_email
from utils.hash import Hash

router = APIRouter(prefix='/auth', tags=['authentication'])


@router.post('/signup', status_code=status.HTTP_201_CREATED)
def signup(request: CreateUser, db: Session = Depends(get_db)):
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

    return {
        'success': True,
        'message': 'User created successfully',
    }

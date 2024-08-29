from typing import Annotated, Tuple

from fastapi import APIRouter, Depends, HTTPException
from pyexpat.errors import messages
from starlette.status import HTTP_200_OK

from auth.oauth import get_current_user
from db.schemas.user_schema import UserBaseOut

router = APIRouter(prefix='/users', tags=['Users'])


@router.post('/profile', status_code=HTTP_200_OK)
def get_profile(user: Annotated[UserBaseOut, Depends(get_current_user)]):
    return {
        'success': True,
        'message': 'User profile retrieved',
        'data': user
    }




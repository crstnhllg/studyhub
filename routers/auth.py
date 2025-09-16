from fastapi.security import OAuth2PasswordRequestForm
from schemas.user import CreateUserRequest, UserResponse
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException
from models import User
from sqlalchemy import or_
from starlette import status
from typing import Annotated
from database import get_db
from sqlalchemy.orm import Session
from core.security import create_access_token, bcrypt_context


router = APIRouter(
    prefix='/auth',
    tags=['Auth']
)
db_dependency = Annotated[Session, Depends(get_db)]

def check_user_duplicate(db: Session, email: str, username: str) -> bool:
    user_exist = db.query(User).filter(or_(
        User.email == email, User.username == username
    )).first()

    return user_exist is not None


@router.post('/', status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency, create_user_request: CreateUserRequest) -> UserResponse:

    if check_user_duplicate(db, create_user_request.email, create_user_request.username):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Email/username already exists!')

    user_data = create_user_request.model_dump(exclude={'password'})
    password = bcrypt_context.hash(create_user_request.password)
    user = User(**user_data, hashed_password=password)
    db.add(user)
    db.commit()
    db.refresh(user)

    return UserResponse(
        id=user.id,
        email=user.email,
        username=user.username,
        created_at=user.created_at
    )


@router.post('/token', status_code=status.HTTP_200_OK)
async def login_for_access_token(db: db_dependency, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = db.query(User).filter(User.username == form_data.username).first()

    if not user or not bcrypt_context.verify(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authentication failed!')

    token = create_access_token(user.username, user.id, timedelta(minutes=60))

    return {
        'access_token': token,
        'token_type': 'bearer'
    }
from app.core.security import create_access_token, hash_password, validate_password
from app.schemas.user import CreateUserRequest, CurrentUserResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import APIRouter, Depends, HTTPException
from app.core.utils import validate_unique_email, validate_unique_username
from app.database import db_dependency
from datetime import timedelta
from starlette import status
from typing import Annotated
from app.models import User



router = APIRouter(
    prefix='/auth',
    tags=['Auth']
)


@router.post('/', status_code=status.HTTP_201_CREATED)
def create_user(db: db_dependency, user_request: CreateUserRequest) -> CurrentUserResponse:
    """
    Create a new user with a hashed password.
    """
    validate_unique_username(db, user_request.username)
    validate_unique_email(db, user_request.email)

    user_data = user_request.model_dump(exclude={'password'})
    password = hash_password(user_request.password)
    user = User(**user_data, hashed_password=password)

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


@router.post('/token', status_code=status.HTTP_200_OK)
def login_for_access_token(db: db_dependency, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    """
    Authenticate a user and return a JWT access token.
    """
    current_user = db.query(User).filter(User.username == form_data.username).first()
    if current_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid username'
        )

    validate_password(form_data.password, current_user.hashed_password)
    token = create_access_token(current_user.username, current_user.id, timedelta(minutes=60))

    return {
        'access_token': token,
        'token_type': 'bearer'
    }
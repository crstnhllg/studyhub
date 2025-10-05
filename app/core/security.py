from datetime import timedelta, datetime, timezone
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException
from passlib.context import CryptContext
from app.database import db_dependency
from jose import jwt, JWTError
from dotenv import load_dotenv
from typing import Annotated
from starlette import status
from app.models import User
import os



load_dotenv()

SECRET_KEY = os.getenv('KEY')
ALGORITHM = 'HS256'

oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


def create_access_token(username: str, user_id: int, expires: timedelta) -> str:
    """
    Generate a JWT access token for the given user with an expiration time.
    """
    expires = datetime.now(timezone.utc) + expires
    encode = {
        'sub': username,
        'user_id': user_id,
        'exp': expires
    }
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(db: db_dependency, token: Annotated[str, Depends(oauth2_bearer)]) -> User:
    """
    Decode the JWT token and retrieve the current authenticated user.
    Raise HTTP 401 Unauthorized if authentication fails.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Authentication failed!'
        )

    current_user = db.get(User, payload.get('user_id'))
    if current_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Authentication failed'
        )

    return current_user


def validate_password(input_password: str, hashed_password: str) -> None:
    """
    Validate the given password against the stored hash.
    Raise HTTP 401 Unauthorized if the password is invalid.
    """
    if not bcrypt_context.verify(input_password, hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid password'
        )


def hash_password(input_password: str) -> str:
    """
    Hash the given password.
    """
    return bcrypt_context.hash(input_password)



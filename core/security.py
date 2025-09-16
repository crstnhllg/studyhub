from datetime import timedelta, datetime, timezone
from jose import jwt, JWTError
from typing import Annotated
from fastapi import Depends, HTTPException
from schemas.user import CurrentUserResponse
from starlette import status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from dotenv import load_dotenv
import os


load_dotenv()

SECRET_KEY = os.getenv('KEY')
ALGORITHM = 'HS256'

oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


def create_access_token(username: str, user_id: int, expires: timedelta) -> str:
    expires = datetime.now(timezone.utc) + expires
    encode = {
        'sub': username,
        'user_id': user_id,
        'exp': expires
    }
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]) -> CurrentUserResponse:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        required_fields = ['sub', 'user_id']

        if any(payload.get(field) is None for field in required_fields):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authentication failed!')

    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authentication failed!')

    return CurrentUserResponse(
        username=payload.get('sub'),
        user_id=payload.get('user_id')
    )


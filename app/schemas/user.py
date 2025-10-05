from pydantic import BaseModel, Field, constr, EmailStr
from app.schemas.base import APIModel
from datetime import datetime



class CreateUserRequest(BaseModel):
    email: EmailStr = Field(examples=['john_doe@example.com'])
    username: constr(min_length=3, max_length=250, strip_whitespace=True) = Field(examples=['john_doe'])
    password: constr(min_length=3, max_length=250, strip_whitespace=True) = Field(examples=['your_password123'])


class ChangeEmailRequest(BaseModel):
    new_email: EmailStr = Field(examples=['example@email.com'])
    password: constr(min_length=3, max_length=250, strip_whitespace=True)


class ChangePassRequest(BaseModel):
    old_password: constr(min_length=3, max_length=250, strip_whitespace=True)
    new_password: constr(min_length=3, max_length=250, strip_whitespace=True)


class DeleteAccountRequest(BaseModel):
    password: constr(min_length=3, max_length=250, strip_whitespace=True)



class CurrentUserResponse(APIModel):
    id: int
    email: str
    username: str
    created_at: datetime

class UserMembershipResponse(APIModel):
    user_id: int
    group_id: int
    role: str
    joined_at: datetime




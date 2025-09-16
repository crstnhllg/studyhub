from pydantic import BaseModel, Field, constr, EmailStr
from datetime import datetime


class CreateUserRequest(BaseModel):
    email: str = Field(max_length=250, examples=['example@email.com'])
    username: constr(min_length=3, max_length=250, strip_whitespace=True) = Field(examples=['john_doe'])
    password: constr(min_length=3, max_length=250, strip_whitespace=True) = Field(examples=['your_password123'])


class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    created_at: datetime


class CurrentUserResponse(BaseModel):
    username: str
    user_id: int

    model_config = {
        "from_attributes": True
    }


class MembershipResponse(BaseModel):
    group_id: int
    group_name: str
    role: str

class MessageResponse(BaseModel):
    success: bool
    message: str


class ChangeEmailRequest(BaseModel):
    new_email: str = Field(max_length=250, examples=['example@email.com'])
    password: constr(min_length=3, max_length=250, strip_whitespace=True)


class ChangePassRequest(BaseModel):
    old_password: constr(min_length=3, max_length=250, strip_whitespace=True)
    new_password: constr(min_length=3, max_length=250, strip_whitespace=True)


class DeleteAccountRequest(BaseModel):
    password: constr(min_length=3, max_length=250, strip_whitespace=True)


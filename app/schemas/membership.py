from pydantic import BaseModel, constr
from app.schemas.base import APIModel


class MembershipResponse(APIModel):
    user_id: int
    username: str
    role: str


class UpdateRoleResponse(APIModel):
    user_id: int
    group_id: int
    role: str


class MemberUpdateRequest(BaseModel):
    role: constr(min_length=3, max_length=250, strip_whitespace=True)
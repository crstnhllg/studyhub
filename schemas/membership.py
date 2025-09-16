from pydantic import BaseModel, constr


class MembershipResponse(BaseModel):
    user_id: int
    username: str
    role: str


class MemberUpdateRequest(BaseModel):
    role: constr(min_length=3, max_length=250, strip_whitespace=True)
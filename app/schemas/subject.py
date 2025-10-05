from pydantic import BaseModel, constr
from app.schemas.base import APIModel



class SubjectRequest(BaseModel):
    name: constr(min_length=3, max_length=250)


class SubjectResponse(APIModel):
    id: int
    name: str
    group_id: int


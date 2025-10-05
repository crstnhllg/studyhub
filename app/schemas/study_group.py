from pydantic import BaseModel, Field, constr
from app.schemas.base import APIModel
from datetime import datetime



class GroupRequest(BaseModel):
    name: constr(min_length=3, max_length=250) = Field(examples=['A New Group Name'])
    description: str = Field(examples=['Some description.'])


class GroupTransferRequest(BaseModel):
    new_owner_id: int = Field(gt=0)


class GroupResponse(APIModel):
    id: int
    name: str
    description: str
    owner_id: int
    created_at: datetime
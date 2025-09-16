from datetime import datetime
from pydantic import BaseModel, Field, constr


class GroupRequest(BaseModel):
    name: constr(min_length=3, max_length=250)
    description: str


class GroupResponse(BaseModel):
    name: str
    description: str
    created_at: datetime

    model_config = {
        "from_attributes": True
    }
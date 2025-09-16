from typing import Optional
from pydantic import BaseModel, Field, constr
from datetime import datetime


class SessionResponse(BaseModel):
    title: str
    description: str
    date_time: datetime
    duration: int
    status: str
    subject: str

    model_config = {
        "from_attributes": True
    }


class SessionRequest(BaseModel):
    title: constr(min_length=3, max_length=250)
    description: str
    date_time: datetime = Field(examples=["2025-12-25T10:00:00"])
    duration: int = Field(gt=0)
    status: str = Field(max_length=100)


class SessionUpdateRequest(BaseModel):
    title: Optional[constr(min_length=3, max_length=250)]
    description: Optional[str]
    date_time: Optional[datetime]
    duration: Optional[int] = Field(gt=0)
    status: Optional[str]

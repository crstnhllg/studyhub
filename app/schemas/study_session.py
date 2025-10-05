from pydantic import BaseModel, Field, constr, field_validator
from app.schemas.base import APIModel
from datetime import datetime



class SessionRequest(BaseModel):
    title: constr(min_length=3, max_length=250)
    description: str
    date_time: datetime = Field(examples=['2025-12-12 10:00'])
    duration: int = Field(gt=0)
    status: str = Field(max_length=100)

    @field_validator('date_time', mode='before')
    def parse_datetime(cls, value):
        if isinstance(value, datetime):
            return value
        try:
            return datetime.strptime(value, '%Y-%m-%d %H:%M')
        except ValueError:
            raise ValueError('Date must be in format YYYY-MM-DD HH:MM')


class SessionResponse(APIModel):
    id: int
    title: str
    description: str
    date_time: datetime
    duration: int
    status: str
    subject_id: int

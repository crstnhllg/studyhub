from pydantic import BaseModel, field_serializer, ConfigDict
from datetime import datetime

class APIModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    @field_serializer("*", when_used="json")
    def serialize_datetime(self, value, _info):
        if isinstance(value, datetime):
            return value.strftime("%b %d, %Y %I:%M %p")
        return value
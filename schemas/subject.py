from pydantic import BaseModel, constr


class SubjectResponse(BaseModel):
    name: str
    group_id: int

    model_config = {
        "from_attributes": True
    }


class SubjectRequest(BaseModel):
    name: constr(min_length=3, max_length=250)
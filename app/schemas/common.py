from app.schemas.base import APIModel


class MessageResponse(APIModel):
    success: bool
    message: str
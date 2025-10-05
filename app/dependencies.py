from typing import Annotated
from fastapi import Depends
from app.models import User
from app.core.security import get_current_user

user_dependency = Annotated[User, Depends(get_current_user)]

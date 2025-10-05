from app.routers import auth, users, study_groups, memberships, subjects, study_sessions
from app.database import engine
from fastapi import FastAPI
from app.models import Base


app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(study_groups.router)
app.include_router(memberships.router)
app.include_router(subjects.router)
app.include_router(study_sessions.router)




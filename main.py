from fastapi import FastAPI
from database import engine
import models
from routers import auth, users, study_groups, memberships, subjects, study_sessions


app = FastAPI()

models.Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(study_groups.router)
app.include_router(memberships.router)
app.include_router(subjects.router)
app.include_router(study_sessions.router)




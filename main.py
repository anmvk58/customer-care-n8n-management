from fastapi import FastAPI
from starlette.staticfiles import StaticFiles

import models
from database import engine

from routers import auth
from pages import page_auth

app = FastAPI()

# Create tables from models (if not exists)
models.Base.metadata.create_all(bind=engine)

# Register router to App
app.include_router(auth.router)
app.include_router(page_auth.router)

app.mount("/static", StaticFiles(directory="static"), name="static")  
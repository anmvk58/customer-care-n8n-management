from fastapi import FastAPI, Request
from starlette import status
from starlette.responses import RedirectResponse
from starlette.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import models
from database import engine

from routers import auth, msb_event
from pages import page_auth, page_msb_event
from services.auth_service import get_current_user, redirect_to_login

app = FastAPI()

# Create tables from models (if not exists)
models.Base.metadata.create_all(bind=engine)

# Register router to App
app.include_router(auth.router)
app.include_router(page_auth.router)
app.include_router(page_msb_event.router)
app.include_router(msb_event.router)

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


@app.get("/")
async def home_page(request: Request):
    try:
        user = await get_current_user(request.cookies.get("access_token"))
        return templates.TemplateResponse(name="common_page/home.html",
                                          context={
                                              "request": request,
                                              "user": user
                                          })

    except Exception as e:
        print(e)
        return redirect_to_login()

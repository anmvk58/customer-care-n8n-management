from datetime import timedelta, datetime, timezone
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session
from starlette import status
from database import SessionLocal, get_db
from models import Users
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError, ExpiredSignatureError
from fastapi.templating import Jinja2Templates

from services.auth_service import get_current_user, redirect_to_login

router = APIRouter(
    prefix='/msb-event',
    tags=['msb-event-page']
)

db_dependency = Annotated[Session, Depends(get_db)]

templates = Jinja2Templates(directory="templates")


### Pages ###
@router.get('/list-event', name="msb_event_list_event")
async def render_msb_event_page_list_event(request: Request):
    try:
        user = await get_current_user(request.cookies.get("access_token"))

        if user is None:
            return redirect_to_login()

        return templates.TemplateResponse(name="msb_event_page/list-event.html",
                                          context={
                                              "request": request,
                                              "user": user
                                          })
    except Exception as e:
        print(e)
        return redirect_to_login()
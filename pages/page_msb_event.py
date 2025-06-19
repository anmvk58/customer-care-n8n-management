from datetime import timedelta, datetime, timezone
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session
from starlette import status
from database import SessionLocal, get_db
from models import Users, CompanyEventScheduler
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


@router.get('/create-event', name="msb_event_create_event")
async def render_msb_event_page_create_event(request: Request):
    try:
        user = await get_current_user(request.cookies.get("access_token"))

        if user is None:
            return redirect_to_login()

        return templates.TemplateResponse(name="msb_event_page/create-event.html",
                                          context={
                                              "request": request,
                                              "user": user
                                          })
    except Exception as e:
        print(e)
        return redirect_to_login()


# Render page details event
@router.get('/list-event/{event_id}')
async def render_msb_event_page_detail_event(request: Request, db: db_dependency, event_id: int):
    try:
        user = await get_current_user(request.cookies.get("access_token"))

        if user is None:
            return redirect_to_login()

        event_model: CompanyEventScheduler = db.query(CompanyEventScheduler).filter(CompanyEventScheduler.id == event_id).first()

        event_date = datetime(event_model.event_year, event_model.event_month, event_model.event_day)
        formatted_event_date = event_date.strftime('%m/%d/%Y')

        return templates.TemplateResponse(name="msb_event_page/details-event.html",
                                          context={
                                              "request": request,
                                              "event_model": event_model,
                                              "event_date": formatted_event_date,
                                              "user": user
                                          })


    except Exception as e:
        print(e)
        return redirect_to_login()
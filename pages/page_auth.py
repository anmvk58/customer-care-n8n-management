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

router = APIRouter(
    prefix='/auth',
    tags=['auth-page']
)

SECRET_KEY = '197b2c37c391bed93fe80344fe73b806947a65e36206e05a1a23c2fa12702fe3'
ALGORITHM = 'HS256'

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')


db_dependency = Annotated[Session, Depends(get_db)]

templates = Jinja2Templates(directory="templates")

### Pages ###
@router.get('/login-page', name="login")
def render_login_page(request: Request):
    return templates.TemplateResponse(name="common_page/login.html", request=request)
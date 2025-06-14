from typing import Annotated

from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from starlette import status

from database import get_db
from models import Users
from services.auth_service import authenticate_user, create_access_token, create_refresh_token, \
    verify_token_and_get_payload, get_current_user

router = APIRouter(
    prefix='/auth',
    tags=['auth-api']
)

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

### Models ###
class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = 'bearer'

class RefreshRequest(BaseModel):
    refresh_token: str

class CreateUserRequest(BaseModel):
    username: str
    email: str
    first_name: str
    last_name: str
    password: str
    role: str
    department: str
    phone_number: str


### Endpoints ###
# Define apis below

# Api for create new system
@router.post("/create-user", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency, create_user_request: CreateUserRequest):
    create_user_model = Users(
        email=create_user_request.email,
        username=create_user_request.username,
        first_name=create_user_request.first_name,
        last_name=create_user_request.last_name,
        hashed_password=bcrypt_context.hash(create_user_request.password),
        role=create_user_request.role,
        department=create_user_request.department,
        phone_number=create_user_request.phone_number,
        is_active=True
    )

    db.add(create_user_model)
    db.commit()
    return {
        'error': '',
        'message': 'Tạo mới user thành công !'
    }


# Api get token
@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency):
    result = authenticate_user(form_data.username, form_data.password, db)

    # If any error ?
    if len(result.get('error_code')) > 0:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail=result.get('error_code'))

    user : Users = result.get('user')
    access_token = create_access_token(username = user.username,
                                       user_id=user.id,
                                       last_name=user.last_name,
                                       first_name=user.first_name,
                                       role=user.role)

    refresh_token = create_refresh_token(username=user.username,
                                         user_id=user.id,
                                         role=user.role)

    return Token(access_token=access_token, refresh_token=refresh_token)


# Api for renew token by refresh_token
@router.post("/refresh", response_model=Token)
def refresh_token(db: db_dependency, refresh_req: RefreshRequest):
    payload = verify_token_and_get_payload(refresh_req.refresh_token, token_type="refresh")

    if not payload:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    user_id : int = int(payload["id"])
    user = db.query(Users).filter(Users.id.__eq__(user_id), Users.is_active.is_(True)).first()

    new_access_token = create_access_token(username=user.username,
                                       user_id=user.id,
                                       last_name=user.last_name,
                                       first_name=user.first_name,
                                       role=user.role)

    new_refresh_token = create_refresh_token(username=user.username,
                                         user_id=user.id,
                                         role=user.role)

    return Token(access_token=new_access_token, refresh_token=new_refresh_token)


# Api for test authentication
@router.get("/test_auth")
def test_auth_system(user: user_dependency,
                    db: db_dependency,
                    user_id: int):
    print("api 1")
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authentication Failed')

    return db.query(Users).filter_by(id=user_id).first()
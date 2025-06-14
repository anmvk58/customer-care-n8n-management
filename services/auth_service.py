from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError, ExpiredSignatureError
from passlib.context import CryptContext
from starlette import status

from models import Users

# Constant for JWT config
SECRET_KEY = "197b2c37c391bed93fe80344fe73b806947a65e36206e05a1a23c2fa12702fe3"
ALGORITHM = "HS256"

# Constant for config expire token
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Context for bcrypt
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')


def create_access_token(username: str, user_id: int, first_name: str, last_name: str, role: str):
    """
    Function to create access_token. Data usually use in application should embed inside token
    :return: access_token
    """
    encode_data = {
        'sub': username,
        'id': user_id,
        'first_name': first_name,
        'last_name': last_name,
        'role': role
    }

    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    encode_data.update({"exp": expire, "type": "access"})
    return jwt.encode(encode_data, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(username: str, user_id: int, role: str):
    """
    Function to create refresh_token. Data to recognize and return back access_token
    :return: refresh_token
    """
    encode_data = {
        'sub': username,
        'id': user_id,
        'role': role
    }
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    encode_data.update({"exp": expire, "type": "refresh"})
    return jwt.encode(encode_data, SECRET_KEY, algorithm=ALGORITHM)


def verify_token_and_get_payload(token: str, token_type: str = "access"):
    """
    Function to verify token type and return payload
    :param token: token from client header
    :param token_type: type of token: access | refresh
    :return: payload of token after decode
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != token_type:
            raise JWTError("Invalid token type")
        return payload
    except JWTError:
        return None


def authenticate_user(username: str, password: str, db):
    """
    Function to authenticate user via username and password form
    :param username: username of user
    :param password: password of user
    :param db: database to work with
    :return: user
    """
    user = db.query(Users).filter(Users.username == username, Users.is_active == True).first()

    # user is not exists or inactive
    if not user:
        return {
            'error_code': 'USER_NOT_EXISTS',
            'user': None
        }

    # wrong password
    if not bcrypt_context.verify(password, user.hashed_password):
        return {
            'error_code': 'NOT_AUTH_PASS',
            'user': None
        }

    return {
        'error_code': '',
        'user': user
    }


# function for validate user in anywhere anytime
async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    """
    Function for validate user when client call api with access_token
    :param token: access_token
    :return: user (data after decode access_token)
    """
    try:
        if token is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing token in Authorization header",
            )

        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        username: str = payload.get('sub')
        user_id: int = payload.get('id')
        first_name: str = payload.get('first_name')
        last_name: str = payload.get('last_name')
        role: str = payload.get('role')

        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could_not_validate_user')

        return {'username': username, 'id': user_id, 'first_name': first_name, 'last_name': last_name, 'role': role}

    except ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Access_token_expired')
    except Exception as e:
        print(e)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could_not_validate_user')


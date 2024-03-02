import os

import redis
from otp import TwoFactorAuth
import dotenv
from pathlib import Path
from typing import Union
from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone

from jose import jwt, JWTError

from pydantic import EmailStr
from database import MySQLDatabase
from models import User, UserCreate, TokenData

BASE_DIR = Path(__file__).resolve().parent.parent
dotenv.load_dotenv(BASE_DIR / ".env")

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

outh2_scheme = OAuth2PasswordBearer(tokenUrl="token")

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def create_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_user(user_id_or_email: Union[int, str]) -> UserCreate:
    with MySQLDatabase() as db:
        if isinstance(user_id_or_email, int):
            db.cursor.execute("select * from user where sid = %s", (user_id_or_email,))
        else:
            db.cursor.execute(
                "select * from user where email = %s", (user_id_or_email,)
            )
        user_data = db.cursor.fetchone()
        if not user_data:
            raise HTTPException(status_code=401, detail="user not found in database")
        return UserCreate(**user_data)


async def get_user_by_email(email: EmailStr) -> UserCreate:
    return await get_user(email)


async def get_user_by_id(sid: int) -> UserCreate:
    return await get_user(sid)


async def get_current_user(token: Annotated[str, Depends(outh2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[
                ALGORITHM,
            ],
        )
        email = payload.get("sub")
        sid = payload.get("sid")
        if email is None:
            raise credentials_exception
        token_data = TokenData(sid=sid, email=email)
    except JWTError:
        raise credentials_exception
    user = await get_user_by_email(token_data.email)
    if user is None:
        raise credentials_exception
    return user

def verify_new_user(user: UserCreate):
    with MySQLDatabase() as db:
        db.cursor.execute("select * from user where email = %s", (user.email,))
        user_db = db.cursor.fetchone()
        if user_db:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="user already exists"
            )
        return user

def verify_otp_new_user(email: EmailStr, otp: int):
    tfa_object = TwoFactorAuth(email, TwoFactorAuth.get_or_create_secret_key(email))
    return tfa_object.verify_totp_code(str(otp))
        


def create_user(user: UserCreate):
    with MySQLDatabase() as db:
        password = pwd_context.hash(user.password)
        db.cursor.execute(
            "insert into user (email, firstname, lastname, password) values (%s,%s,%s,%s)",
            (user.email, user.firstname, user.lastname, password),
        )
        db.connection.commit()

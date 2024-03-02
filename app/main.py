from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException
from pydantic import EmailStr
from otp_email import send_email
from otp import TwoFactorAuth
from fastapi.middleware.cors import CORSMiddleware

from fastapi.security import (
    OAuth2PasswordRequestForm,
)
from utils import (
    create_token,
    create_user,
    get_current_user,
    get_user_by_email,
    verify_password,
    verify_new_user,
    verify_otp_new_user
)

from models import (
    CourseCreate,
    ProfessorCreate,
    TaskCreate,
    UserLogin,
    UserCreate,
    ProjectCreate,
    Token,
)


app = FastAPI()

origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/token")
async def get_token(forrm_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user: UserCreate = await get_user_by_email(forrm_data.username)
    if not verify_password(forrm_data.password, user.password):
        raise HTTPException(status_code=400, detail="password did not match")
    access_token = create_token(data={"sid": user.sid, "sub": user.email})
    return Token(access_token=access_token, token_type="bearer")


@app.post("/otp")
async def sent_otp_new_user(email: EmailStr):
    secret_key = TwoFactorAuth.get_or_create_secret_key(email)
    tfa_object = TwoFactorAuth(email, secret_key)
    send_email(email, tfa_object.totp.now())
    return {"otp_sent": True}

@app.get("/test")
async def test():
    return {"status": "working"}


@app.get("/me")
async def get_about_user(
    current_user: Annotated[UserCreate, Depends(get_current_user)]
):
    return current_user


@app.post("/login")
async def login(user: UserLogin):
    return {"details": user}


@app.post("/signup")
async def signup(user: Annotated[UserCreate, Depends(verify_new_user)], otp: int):
    if verify_otp_new_user(user.email, otp):
        try:
            create_user(user)
            return {"status": "success"}
        except Exception:
            return {"status": "failed"}
    return {"status": "otp is wrong"}


@app.post("/projects")
async def create_project(project: ProjectCreate):
    return {"stored_data": project}


@app.get("/projects")
async def get_project():
    return {"status" "working"}


@app.post("/courses")
async def create_course(course: CourseCreate):
    return {"stored_data": course}


@app.get("/courses")
async def get_course():
    return {"status": "working"}


@app.post("/professors")
async def create_professor(professor: ProfessorCreate):
    return {"stored_data": professor}


@app.get("/professors")
async def get_professor():
    return {"status": "professor received"}


@app.post("/tasks")
async def create_task(task: TaskCreate):
    return {"stored_data": task}


@app.get("/tasks")
async def get_task():
    return {"status": "task received"}

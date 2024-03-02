from enum import Enum
from pydantic import BaseModel, EmailStr
from datetime import datetime

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    sid: int
    email: EmailStr

class StatusEnum(str, Enum):
    planning = "planing"
    active = "active"
    complete = "complete"
    overdue = "overdue"


class UserBase(BaseModel):
    sid: int | None = None
    email: EmailStr


class User(UserBase):
    firstname: str
    lastname: str


class UserLogin(UserBase):
    password: str


class UserCreate(UserBase):
    firstname: str
    lastname: str
    password: str



class ProjectCreate(BaseModel):
    name: str
    course: str
    professor: str
    description: str | None = None
    start: datetime = datetime.now()
    end: datetime
    status: StatusEnum = StatusEnum.planning


class Project(ProjectCreate):
    pid: int


class CourseCreate(BaseModel):
    name: str
    department: str


class Course(CourseCreate):
    cid: int


class ProfessorCreate(BaseModel):
    name: str
    email: EmailStr


class Professor(ProfessorCreate):
    prid: int


class TaskCreate(BaseModel):
    pid: int
    name: str
    description: str | None = None
    sid: int
    end: datetime
    status: StatusEnum = StatusEnum.planning


class Task(TaskCreate):
    tid: int

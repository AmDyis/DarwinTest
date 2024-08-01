from pydantic import BaseModel
from typing import Optional

class UserCreate(BaseModel):
    username: str
    password: str

class User(BaseModel):
    id: int
    username: str

    class Config:
        orm_mode = True

class TaskCreate(BaseModel):
    title: str
    description: str

class Task(BaseModel):
    id: int
    title: str
    description: str
    owner_id: int

    class Config:
        orm_mode = True

from pydantic import BaseModel

class TaskPermissionBase(BaseModel):
    task_id: int
    user_id: int = None
    username: str = None
    can_read: bool = False
    can_update: bool = False
    can_delete: bool = False

class TaskPermission(TaskPermissionBase):
    id: int

class PermissionResponse(BaseModel):
    message: str
    permission: TaskPermission

class TaskPermission(TaskPermissionBase):
    id: int

    class Config:
        orm_mode = True

class LoginResponse(BaseModel):
    message: str
    user: User

class RegisterResponse(BaseModel):
    message: str
    user: User

class PermissionResponse(BaseModel):
    message: str
    permission: TaskPermission

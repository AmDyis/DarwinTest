import asyncpg
import schemas, database
from passlib.context import CryptContext
from fastapi import HTTPException

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except ValueError:
        raise HTTPException(status_code=400, detail="Hash could not be identified")

async def get_user_by_id(user_id: int):
    conn = await database.get_connection()
    user = await conn.fetchrow("SELECT id, username FROM Users WHERE id = $1", user_id)
    await conn.close()
    return user

async def get_user_by_username(username: str):
    conn = await database.get_connection()
    user = await conn.fetchrow("SELECT id, username, password FROM Users WHERE username = $1", username)
    await conn.close()
    return user

async def get_user_id_by_username(username: str):
    conn = await database.get_connection()
    try:
        user = await conn.fetchrow("SELECT id FROM Users WHERE username = $1", username)
        return user['id'] if user else None
    finally:
        await conn.close()

async def create_user(user: schemas.UserCreate):
    conn = await database.get_connection()
    hashed_password = pwd_context.hash(user.password)
    user_db = await conn.fetchrow("INSERT INTO Users (username, password) VALUES ($1, $2) RETURNING id, username",
                                  user.username, hashed_password)
    await conn.close()
    return user_db

async def create_task(task: schemas.TaskCreate, user_id: int):
    conn = await database.get_connection()
    task_db = await conn.fetchrow(
        "INSERT INTO Tasks (title, description, owner_id) VALUES ($1, $2, $3) RETURNING id, title, description, owner_id",
        task.title, task.description, user_id)
    await conn.close()
    return task_db

async def update_task(task_id: int, task: schemas.TaskCreate):
    conn = await database.get_connection()
    task_db = await conn.fetchrow(
        "UPDATE Tasks SET title = $1, description = $2 WHERE id = $3 RETURNING id, title, description, owner_id",
        task.title, task.description, task_id)
    await conn.close()
    return task_db

async def give_task_permission(permission: schemas.TaskPermissionBase):
    conn = await database.get_connection()
    if permission.username:
        user_id = await get_user_id_by_username(permission.username)
        if not user_id:
            raise HTTPException(status_code=404, detail="User not found")
        permission.user_id = user_id

    permission_db = await conn.fetchrow(
        "INSERT INTO Tasks_Permission (task_id, user_id, can_read, can_update, can_delete) VALUES ($1, $2, $3, $4, $5) RETURNING id, task_id, user_id, can_read, can_update, can_delete",
        permission.task_id, permission.user_id, permission.can_read, permission.can_update, permission.can_delete)
    await conn.close()
    return permission_db

async def get_task_permissions(task_id: int):
    conn = await database.get_connection()
    permissions = await conn.fetch(
        "SELECT id, task_id, user_id, can_read, can_update, can_delete FROM Tasks_Permission WHERE task_id = $1", task_id)
    await conn.close()
    return permissions

async def get_task_permission_for_user(task_id: int, user_id: int):
    conn = await database.get_connection()
    permission = await conn.fetchrow(
        "SELECT id, task_id, user_id, can_read, can_update, can_delete FROM Tasks_Permission WHERE task_id = $1 AND user_id = $2",
        task_id, user_id)
    await conn.close()
    return permission

async def get_task_by_id(task_id: int):
    conn = await database.get_connection()
    task = await conn.fetchrow("SELECT id, title, description, owner_id FROM Tasks WHERE id = $1", task_id)
    await conn.close()
    return task

async def get_tasks():
    conn = await database.get_connection()
    tasks = await conn.fetch("SELECT id, title, description, owner_id FROM Tasks")
    await conn.close()
    return tasks

async def authenticate_user(username: str, password: str):
    user = await get_user_by_username(username)
    if not user or not verify_password(password, user['password']):
        return False
    return user

async def delete_task(task_id: int):
    conn = await database.get_connection()
    await conn.execute("DELETE FROM Tasks WHERE id = $1", task_id)
    await conn.close()

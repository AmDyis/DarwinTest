from fastapi import FastAPI, HTTPException, Depends, Request, Response, status
import schemas, crud
from typing import List

app = FastAPI()

async def authenticate_user(username: str, password: str):
    user = await crud.authenticate_user(username, password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    return schemas.User(id=user['id'], username=user['username'])

@app.post("/register/", response_model=schemas.RegisterResponse)
async def register_user(user: schemas.UserCreate):
    db_user = await crud.get_user_by_username(user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    user_db = await crud.create_user(user)
    return schemas.RegisterResponse(message="User created successfully",
                                    user=schemas.User(id=user_db['id'], username=user_db['username']))

@app.post("/login/", response_model=schemas.LoginResponse)
async def login_user(user: schemas.UserCreate, response: Response):
    authenticated_user = await authenticate_user(user.username, user.password)
    response.set_cookie(key="username", value=user.username)
    response.set_cookie(key="password", value=user.password)
    return schemas.LoginResponse(message="Login successful", user=authenticated_user)

async def get_current_user(request: Request):
    username = request.cookies.get("username")
    password = request.cookies.get("password")
    if not username or not password:
        raise HTTPException(status_code=401, detail="Not authenticated")
    user = await crud.authenticate_user(username, password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    return schemas.User(id=user['id'], username=user['username'])

@app.put("/tasks/{task_id}", response_model=schemas.Task)
async def update_task(task_id: int, task: schemas.TaskCreate, current_user: schemas.User = Depends(get_current_user)):
    db_task = await crud.get_task_by_id(task_id)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    if db_task['owner_id'] != current_user.id:
        permissions = await crud.get_task_permissions(task_id)
        user_permission = next((p for p in permissions if p['user_id'] == current_user.id), None)
        if not user_permission or not user_permission['can_update']:
            raise HTTPException(status_code=403, detail="Not enough permissions to update this task")
    task_db = await crud.update_task(task_id, task)
    return schemas.Task(id=task_db['id'], title=task_db['title'], description=task_db['description'], owner_id=task_db['owner_id'])

@app.get("/tasks/{task_id}", response_model=schemas.Task)
async def read_task(task_id: int, current_user: schemas.User = Depends(get_current_user)):
    task = await crud.get_task_by_id(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    if task['owner_id'] != current_user.id:
        permission = await crud.get_task_permission_for_user(task_id, current_user.id)
        if not permission or not permission['can_read']:
            raise HTTPException(status_code=403, detail="Not enough permissions to read this task")
    return schemas.Task(id=task['id'], title=task['title'], description=task['description'], owner_id=task['owner_id'])

@app.post("/permissions/", response_model=schemas.PermissionResponse)
async def give_task_permission(permission: schemas.TaskPermissionBase,
                               current_user: schemas.User = Depends(get_current_user)):
    user_id = permission.user_id
    if permission.username:
        user = await crud.get_user_by_username(permission.username)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        user_id = user['id']

    if user_id is None:
        raise HTTPException(status_code=400, detail="User ID or username must be provided")

    task = await crud.get_task_by_id(permission.task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    if task['owner_id'] != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions to give permissions for this task")

    permission_db = await crud.give_task_permission(permission=permission)
    return schemas.PermissionResponse(
        message=f"Permission granted successfully for {permission_db['user_id']}",
        permission=schemas.TaskPermission(
            id=permission_db['id'],
            task_id=permission_db['task_id'],
            user_id=permission_db['user_id'],
            can_read=permission_db['can_read'],
            can_update=permission_db['can_update'],
            can_delete=permission_db['can_delete']
        )
    )

@app.get("/users/{username}", response_model=schemas.User)
async def read_user(username: str):
    user = await crud.get_user_by_username(username)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return schemas.User(id=user['id'], username=user['username'])

@app.post("/tasks/", response_model=schemas.Task)
async def create_task(task: schemas.TaskCreate, current_user: schemas.User = Depends(get_current_user)):
    task_db = await crud.create_task(task=task, user_id=current_user.id)
    return schemas.Task(id=task_db['id'], title=task_db['title'], description=task_db['description'], owner_id=task_db['owner_id'])

@app.delete("/tasks/{task_id}", response_model=dict)
async def delete_task(task_id: int, current_user: schemas.User = Depends(get_current_user)):
    task = await crud.get_task_by_id(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    if task['owner_id'] != current_user.id:
        permission = await crud.get_task_permission_for_user(task_id, current_user.id)
        if not permission or not permission['can_delete']:
            raise HTTPException(status_code=403, detail="Not enough permissions to delete this task")

    await crud.delete_task(task_id)
    return {"message": "Task deleted successfully"}

import pytest
from httpx import AsyncClient
from main import app
import schemas, crud

@pytest.mark.asyncio
async def test_register_user():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/register/", json={"username": "testuser", "password": "testpassword"})
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "User created successfully"
        assert data["user"]["username"] == "testuser"

@pytest.mark.asyncio
async def test_login_user():
    async with AsyncClient(app=app, base_url="http://test") as client:
        await client.post("/register/", json={"username": "testuser", "password": "testpassword"})
        response = await client.post("/login/", json={"username": "testuser", "password": "testpassword"})
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Login successful"
        assert data["user"]["username"] == "testuser"

@pytest.mark.asyncio
async def test_create_task():
    async with AsyncClient(app=app, base_url="http://test") as client:
        await client.post("/register/", json={"username": "testuser", "password": "testpassword"})
        login_response = await client.post("/login/", json={"username": "testuser", "password": "testpassword"})
        cookies = login_response.cookies
        response = await client.post("/tasks/", json={"title": "Test Task", "description": "Test Description"}, cookies=cookies)
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Test Task"
        assert data["description"] == "Test Description"

@pytest.mark.asyncio
async def test_update_task():
    async with AsyncClient(app=app, base_url="http://test") as client:
        await client.post("/register/", json={"username": "testuser", "password": "testpassword"})
        login_response = await client.post("/login/", json={"username": "testuser", "password": "testpassword"})
        cookies = login_response.cookies
        create_response = await client.post("/tasks/", json={"title": "Test Task", "description": "Test Description"}, cookies=cookies)
        task_id = create_response.json()["id"]
        response = await client.put(f"/tasks/{task_id}", json={"title": "Updated Task", "description": "Updated Description"}, cookies=cookies)
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Task"
        assert data["description"] == "Updated Description"

@pytest.mark.asyncio
async def test_read_task():
    async with AsyncClient(app=app, base_url="http://test") as client:
        await client.post("/register/", json={"username": "testuser", "password": "testpassword"})
        login_response = await client.post("/login/", json={"username": "testuser", "password": "testpassword"})
        cookies = login_response.cookies
        create_response = await client.post("/tasks/", json={"title": "Test Task", "description": "Test Description"}, cookies=cookies)
        task_id = create_response.json()["id"]
        response = await client.get(f"/tasks/{task_id}", cookies=cookies)
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Test Task"
        assert data["description"] == "Test Description"

@pytest.mark.asyncio
async def test_delete_task():
    async with AsyncClient(app=app, base_url="http://test") as client:
        await client.post("/register/", json={"username": "testuser", "password": "testpassword"})
        login_response = await client.post("/login/", json={"username": "testuser", "password": "testpassword"})
        cookies = login_response.cookies
        create_response = await client.post("/tasks/", json={"title": "Test Task", "description": "Test Description"}, cookies=cookies)
        task_id = create_response.json()["id"]
        response = await client.delete(f"/tasks/{task_id}", cookies=cookies)
        assert response.status_code == 200
        assert response.json() == {"message": "Task deleted successfully"}

@pytest.mark.asyncio
async def test_give_task_permission():
    async with AsyncClient(app=app, base_url="http://test") as client:
        await client.post("/register/", json={"username": "testuser", "password": "testpassword"})
        await client.post("/register/", json={"username": "testuser2", "password": "testpassword2"})
        login_response = await client.post("/login/", json={"username": "testuser", "password": "testpassword"})
        cookies = login_response.cookies
        create_response = await client.post("/tasks/", json={"title": "Test Task", "description": "Test Description"}, cookies=cookies)
        task_id = create_response.json()["id"]
        user2 = await client.get("/users/testuser2")
        user2_id = user2.json()["id"]
        response = await client.post("/permissions/", json={"task_id": task_id, "user_id": user2_id, "can_read": True, "can_update": True}, cookies=cookies)
        assert response.status_code == 200
        data = response.json()
        assert data["permission"]["user_id"] == user2_id
        assert data["permission"]["can_read"]
        assert data["permission"]["can_update"]


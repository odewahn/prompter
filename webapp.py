from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from db import DatabaseManager
from pydantic import BaseModel


class User(BaseModel):
    username: str


app = FastAPI()
app.mount("/static", StaticFiles(directory="static", html=True), name="static")
db_manager = None

def init_db_manager(db_url):
    global db_manager
    db_manager = DatabaseManager(db_url)


@app.post("/users/")
async def create_user(user: User):
    await db_manager.add_user(user.username)
    return {"status": "success", "username": user.username}


@app.get("/api/users", response_model=list[User])
async def get_users():
    users = await db_manager.get_all_users()
    return [user.to_dict() for user in users]

@app.get("/users/", response_class=HTMLResponse)
async def list_users(request: Request):
    users = await db_manager.get_all_users()
    user_list_html = "<ul>" + "".join(f"<li>{user.username}</li>" for user in users) + "</ul>"
    return HTMLResponse(content=f"<html><body><h1>User List</h1>{user_list_html}</body></html>")

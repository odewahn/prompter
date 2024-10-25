from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from db import DatabaseManager, Block
from sqlalchemy import text
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

@app.get("/api/blocks/{block_group_id}", response_model=list[dict])
@app.get("/api/blocks", response_model=list[dict])
async def get_blocks(block_group_id: int = None):
    # Determine the block group to fetch
    async with db_manager.SessionLocal() as session:
        async with session.begin():
            if block_group_id is None:
                current_group = await session.execute(
                    text("SELECT id FROM block_groups WHERE is_current = True")
                )
                block_group_id = current_group.scalar_one_or_none()

                if block_group_id is None:
                    return []

            # Fetch blocks in the specified or current group
            blocks = await session.execute(
                text("SELECT * FROM blocks WHERE block_group_id = :group_id"),
                {"group_id": block_group_id}
            )
            result = blocks.fetchall()

            if not result:
                raise HTTPException(status_code=404, detail="Block group not found")

            return [dict(block.items()) for block in result]
async def list_users(request: Request):
    users = await db_manager.get_all_users()
    user_list_html = "<ul>" + "".join(f"<li>{user.username}</li>" for user in users) + "</ul>"
    return HTMLResponse(content=f"<html><body><h1>User List</h1>{user_list_html}</body></html>")
import asyncio

async def shutdown_webapp():
    # Implement the logic to gracefully shutdown the web application
    print("Shutting down the web application...")
    # Add any necessary cleanup or shutdown logic here
    await asyncio.sleep(1)  # Simulate some async cleanup work
    print("Web application shutdown complete.")

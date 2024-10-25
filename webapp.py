from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from db import DatabaseManager, Block
from sqlalchemy import text
from pydantic import BaseModel


app = FastAPI()
app.mount("/static", StaticFiles(directory="static", html=True), name="static")
db_manager = DatabaseManager(DatabaseManager.current_db_url or "sqlite+aiosqlite:///default.db")


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
                {"group_id": block_group_id},
            )
            result = blocks.mappings().all()

            if not result:
                raise HTTPException(status_code=404, detail="Block group not found")

            return [dict(block) for block in result]



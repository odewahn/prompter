from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from db import DatabaseManager, Block
from sqlalchemy import text
from pydantic import BaseModel


app = FastAPI()

app.mount("/static", StaticFiles(directory="static", html=True), name="static")


@app.get("/api/blocks/{block_group_id}", response_model=dict)
@app.get("/api/blocks", response_model=dict)
async def get_blocks(block_group_id: int = None):
    db_manager = DatabaseManager(DatabaseManager.current_db_url)
    # Determine the block group to fetch
    async with db_manager.SessionLocal() as session:
        async with session.begin():
            if block_group_id is None:
                current_group = await session.execute(
                    text("select * from block_groups where is_current = True")
                )
            else:
                current_group = await session.execute(
                    text("select * from block_groups where id = :group_id"),
                    {"group_id": block_group_id},
                )

            # If current_group is empty, return 404
            current_group_result = current_group.one_or_none()
            if not current_group_result:
                raise HTTPException(status_code=404, detail="Block group not found")

            # Create the response payload, which should be a dictionary where the root keys
            # are the fields from the current_group query, and the values are lists of blocks
            # are an array under the key "blocks"
            result = current_group_result._asdict()
            blocks = await session.execute(
                text("select * from blocks where block_group_id = :group_id"),
                {"group_id": result["id"]},
            )
            result["blocks"] = [block._asdict() for block in blocks]

            return result

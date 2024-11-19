# For pyinstaller, we want to show something as quickly as possible
print("Starting web UI...")
from rich.console import Console
import os

console = Console()

# Find the directory where binary is running
script_path = os.path.dirname(os.path.realpath(__file__))


# Set up a loading message as the libraries are loaded
with console.status(f"[bold green]Loading required libraries...") as status:
    from src.db import DatabaseManager, Block
    from fastapi import FastAPI, Request, HTTPException
    from fastapi.responses import HTMLResponse
    from fastapi.staticfiles import StaticFiles
    from sqlalchemy import text
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)
app.mount(
    "/static",
    StaticFiles(directory=os.path.join(script_path, "static"), html=True),
    name="static",
)


@app.get("/api/blocks/{group_id}", response_model=dict)
@app.get("/api/blocks", response_model=dict)
async def get_blocks(group_id: int = None):
    db_manager = DatabaseManager(DatabaseManager.current_db_url)
    # Determine the block group to fetch
    async with db_manager.SessionLocal() as session:
        async with session.begin():
            if group_id is None:
                current_group = await session.execute(
                    text("select * from groups where is_current = True")
                )
            else:
                current_group = await session.execute(
                    text("select * from groups where id = :group_id"),
                    {"group_id": group_id},
                )

            # If current_group is empty, return 404
            current_group_result = current_group.one_or_none()
            if not current_group_result:
                raise HTTPException(status_code=404, detail="Group not found")

            # Create the response payload, which should be a dictionary where the root keys
            # are the fields from the current_group query, and the values are lists of blocks
            # are an array under the key "blocks"
            result = current_group_result._asdict()
            blocks = await session.execute(
                text("select * from blocks where group_id = :group_id"),
                {"group_id": result["id"]},
            )
            result["blocks"] = [block._asdict() for block in blocks]

            return result

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
    from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
    from fastapi.responses import HTMLResponse
    from fastapi.staticfiles import StaticFiles
    from sqlalchemy import text
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel
    from src.openai_functions import complete
    from fastapi import HTTPException
    import json
    from src.command_handlers import handle_command
    from src.command_parser import create_parser


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


@app.get("/api/blocks/{block_tag}", response_model=dict)
@app.get("/api/blocks", response_model=dict)
async def get_blocks(block_tag: str = None):
    db_manager = DatabaseManager(DatabaseManager.current_db_url)
    # Determine the block group to fetch
    async with db_manager.SessionLocal() as session:
        async with session.begin():
            if block_tag is None:
                current_group = await session.execute(
                    text("select * from groups where is_current = True")
                )
            else:
                current_group = await session.execute(
                    text("select * from groups where tag = :block_tag"),
                    {"block_tag": block_tag},
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


class CompletionRequest(BaseModel):
    block: dict
    task: str
    persona: str
    metadata: dict
    model: str
    temperature: float


@app.post("/api/complete", response_model=dict)
async def complete_prompt(request: CompletionRequest):
    try:
        results = await complete(
            blocks=[request.block],
            task_text=request.task,
            persona_text=request.persona,
            metadata=request.metadata,
            model=request.model,
            temperature=request.temperature,
        )
        return results[0]  # Assuming complete returns a list of results
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/set-current-group", response_model=dict)
async def set_current_group(request: Request):
    data = await request.json()
    tag = data.get("tag")
    if not tag:
        raise HTTPException(status_code=400, detail="Tag is required")

    db_manager = DatabaseManager(DatabaseManager.current_db_url)
    async with db_manager.SessionLocal() as session:
        async with session.begin():
            try:
                await db_manager.set_current_group(tag)
                return {"message": f"Current group set to '{tag}'"}
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/command", response_model=dict)
async def execute_command(request: Request, background_tasks: BackgroundTasks):
    data = await request.json()
    command = data.get("command")
    if not command:
        raise HTTPException(status_code=400, detail="Command is required")

    parser = create_parser()
    try:
        args = parser.parse_args(command.split())
        background_tasks.add_task(handle_command, args, command)
        return {"message": "Command is being processed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def get_groups():
    db_manager = DatabaseManager(DatabaseManager.current_db_url)
    async with db_manager.SessionLocal() as session:
        async with session.begin():
            groups = await session.execute(text("select * from groups"))
            return [group._asdict() for group in groups]

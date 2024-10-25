import asyncio
import sys
from repl_handlers import handle_command, init_db_manager as init_repl_db_manager
import uvicorn
from webapp import app, init_db_manager
from repl import interactive_repl
from prompt_toolkit.patch_stdout import patch_stdout
from db import DatabaseManager
from repl_handlers import init_db_manager as init_repl_db_manager
import logging

# Configure logging
logging.basicConfig(
    filename="app_logs.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - [%(name)s] - %(message)s",
)

# Configure SQLAlchemy logging
sqlalchemy_logger = logging.getLogger("sqlalchemy.engine")
sqlalchemy_logger.setLevel(logging.ERROR)
sqlalchemy_handler = logging.FileHandler("sqlalchemy_logs.log")
sqlalchemy_handler.setFormatter(
    logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
)
sqlalchemy_logger.addHandler(sqlalchemy_handler)


async def initialize_database(db_url):
    db_manager = DatabaseManager(db_url)
    await db_manager.initialize_db()
    init_db_manager(db_url)
    init_repl_db_manager(db_url)


async def main():
    db_url = f"sqlite+aiosqlite:///mydatabase.db"
    await initialize_database(db_url)

    config = uvicorn.Config(
        app=app, host="127.0.0.1", port=8000, loop="asyncio", log_level="warning"
    )
    server = uvicorn.Server(config)

    web_server_task = asyncio.create_task(server.serve())
    with patch_stdout():
        repl_task = asyncio.create_task(interactive_repl())

    try:
        await asyncio.gather(web_server_task, repl_task)
    except ExitREPLException:
        web_server_task.cancel()
        await server.shutdown()


if __name__ == "__main__":
    asyncio.run(main())

# For pyinstaller, we want to show something as quickly as possible
print("Starting prompter...")
from rich.console import Console

console = Console()

# Set up a loading message as the libraries are loaded
with console.status(f"[bold green]Loading required libraries...") as status:
    from src.constants import DEFAULT_DB_URL
    from src.command_handlers import (
        handle_command,
        init_db_manager as init_repl_db_manager,
        ExitREPLException,
    )
    from src.webapp import app
    from src.repl import interactive_repl
    from src.db import DatabaseManager
    from src.command_handlers import init_db_manager as init_repl_db_manager
    import uvicorn
    import asyncio
    import sys
    import logging
    import os
    from prompt_toolkit.patch_stdout import patch_stdout


# Configure logging
logging.basicConfig(
    level=logging.CRITICAL,  # Set root logger to CRITICAL to suppress most logs
    format="%(asctime)s - %(levelname)s - [%(name)s] - %(message)s",
)

# Suppress SQLAlchemy logging
sqlalchemy_logger = logging.getLogger("sqlalchemy")
sqlalchemy_logger.setLevel(logging.CRITICAL)

# Suppress Uvicorn logging
uvicorn_logger = logging.getLogger("uvicorn")
uvicorn_logger.setLevel(logging.CRITICAL)


async def initialize_database(db_url):
    db_manager = DatabaseManager(db_url)
    await db_manager.initialize_db()
    init_repl_db_manager(db_url)


async def main():
    db_url = DEFAULT_DB_URL
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
        # Cancel all running tasks
        tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
        [task.cancel() for task in tasks]
        await asyncio.gather(*tasks, return_exceptions=True)


if __name__ == "__main__":
    # os.chdir("/Users/odewahn/Desktop/cat-essay")
    asyncio.run(main())

# For pyinstaller, we want to show something as quickly as possible
print("Starting prompter...")
from rich.console import Console

console = Console()

# Set up a loading message as the libraries are loaded
with console.status(f"[bold green]Loading required libraries...") as status:
    import asyncio
    import sys
    from command_handlers import (
        handle_command,
        init_db_manager as init_repl_db_manager,
        ExitREPLException,
    )
    import uvicorn
    from webapp import app
    from repl import interactive_repl
    from prompt_toolkit.patch_stdout import patch_stdout
    from db import DatabaseManager
    from command_handlers import init_db_manager as init_repl_db_manager
    import logging
    from constants import DEFAULT_DB_URL
    import os


# Configure logging
logging.basicConfig(
    filename="log_app.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - [%(name)s] - %(message)s",
)

# Configure SQLAlchemy logging
sqlalchemy_logger = logging.getLogger("sqlalchemy.engine")
sqlalchemy_logger.setLevel(logging.ERROR)
sqlalchemy_handler = logging.FileHandler("log_sqlalchemy.log")
sqlalchemy_handler.setFormatter(
    logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
)
sqlalchemy_logger.addHandler(sqlalchemy_handler)


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
        # Stop the event loop
        asyncio.get_event_loop().stop()


if __name__ == "__main__":
    os.chdir("/Users/odewahn/Desktop/cat-essay")
    asyncio.run(main())

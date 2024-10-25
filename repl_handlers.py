from business import BusinessLogic
from db import DatabaseManager
import sys

db_manager = None
business = None


def init_db_manager(db_url):
    global db_manager, business
    db_manager = DatabaseManager(db_url)
    business = BusinessLogic(db_manager)


class ExitREPLException(Exception):
    pass


async def handle_command(args, command):
    command_handlers = {
        "use": handle_use_command,
        "load": handle_load_command,
        "exit": handle_exit_command,
    }

    handler = command_handlers.get(args.command)
    if handler:
        await handler(args, command)
    else:
        print(f"Unknown command: {args.command}")

async def handle_use_command(args, command):
    new_db_url = f"sqlite+aiosqlite:///{args.db_name}.db"
    new_db_manager = DatabaseManager(new_db_url)
    await new_db_manager.initialize_db()
    init_db_manager(new_db_url)
    print(f"Using database: {args.db_name}.db")

async def handle_load_command(args, command):
    files = args.files  # Assume args.files is a list of file paths
    tag = args.tag or "default"
    await business.load_files(files, tag, command)

async def handle_exit_command(args, command):
    print("Exiting...")
    await db_manager.close()
    raise ExitREPLException()

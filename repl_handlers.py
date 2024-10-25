from business import BusinessLogic
from db import DatabaseManager
from webapp import init_db_manager as init_webapp_db_manager
import sys
from webapp import shutdown_webapp

db_manager = None
business = None


def init_db_manager(db_url):
    global db_manager, business
    db_manager = DatabaseManager(db_url)
    business = BusinessLogic(db_manager)


class ExitREPLException(Exception):
    pass

async def handle_command(args):

    if args.command == "use":
        new_db_url = f"sqlite+aiosqlite:///{args.db_name}.db"
        new_db_manager = DatabaseManager(new_db_url)
        await new_db_manager.initialize_db()
        init_db_manager(new_db_url)
        init_webapp_db_manager(new_db_url)
        print(f"Using database: {args.db_name}.db")
    elif args.command == "load":
        files = args.files  # Assume args.files is a list of file paths
        tag = args.group_tag or "default"
        await business.load_files(files, tag)
        print(f"Loaded files into BlockGroup with tag: {tag}")
        print("Exiting...")
        await shutdown_webapp()
        await db_manager.close()
        raise ExitREPLException()

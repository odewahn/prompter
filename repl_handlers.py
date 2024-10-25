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


async def handle_command(args):

    if args.command == "use":
        new_db_url = f"sqlite+aiosqlite:///{args.db_name}.db"
        new_db_manager = DatabaseManager(new_db_url)
        await new_db_manager.initialize_db()
        init_db_manager(new_db_url)
        init_webapp_db_manager(new_db_url)
        print(f"Using database: {args.db_name}.db")
    elif args.command == "exit":
        print("Exiting...")
        await shutdown_webapp()
        sys.exit(0)

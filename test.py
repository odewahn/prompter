import asyncio
from db import DatabaseManager

async def main():
    # Initialize the database manager with a sample database URL
    db_url = "sqlite+aiosqlite:///test.db"
    db_manager = DatabaseManager(db_url)
    
    # Initialize the database (create tables if they don't exist)
    await db_manager.initialize_db()

    # Fetch and print current blocks
    blocks = await db_manager.get_current_blocks()
    for block in blocks:
        print(block)

    # Close the database connection
    await db_manager.close()

if __name__ == "__main__":
    asyncio.run(main())

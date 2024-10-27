import asyncio
from db import DatabaseManager
from constants import DEFAULT_DB_URL
from transformations import apply_transformation


async def main():
    # Initialize the database manager with a sample database URL
    db_manager = DatabaseManager(DEFAULT_DB_URL)

    # Initialize the database (create tables if they don't exist)
    await db_manager.initialize_db()

    # Fetch and print current blocks
    blocks = await db_manager.get_current_blocks()
    for block in blocks[:1]:
        new_block = block.content
        for transformation in ["new-line-split", "sentence-split", "token-split"]:
            new_block = apply_transformation(transformation, new_block, N=5)
        for b in new_block:
            print(f"************\n{b}\n")

    # Close the database connection
    await db_manager.close()


if __name__ == "__main__":
    asyncio.run(main())

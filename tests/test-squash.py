import asyncio
import itertools


# Add the ../src directory to the path
import sys
import os

sys.path.append(os.path.abspath("../src"))

from db import DatabaseManager
from constants import DEFAULT_DB_URL


async def main():
    # Initialize the database manager with a sample database URL
    db_manager = DatabaseManager(DEFAULT_DB_URL)

    # Initialize the database (create tables if they don't exist)
    await db_manager.initialize_db()

    # Fetch and print current blocks
    blocks, headers = await db_manager.get_current_blocks()
    # Use itertools to pull out groups based o the block_tag
    for block_tag, block_group in itertools.groupby(
        blocks, key=lambda x: x["block_tag"]
    ):
        print(f"Block tag: {block_tag}\n\n")
        # join all the content in the block_group
        out = "\n\n".join([block["content"] for block in block_group])
        print(out)

    await db_manager.close()


if __name__ == "__main__":
    asyncio.run(main())

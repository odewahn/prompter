import asyncio
from db import DatabaseManager
from constants import DEFAULT_DB_URL
from transformations import apply_transformation
from db import Group, Block
import json


async def main():
    # Initialize the database manager with a sample database URL
    db_manager = DatabaseManager(DEFAULT_DB_URL)

    # Initialize the database (create tables if they don't exist)
    await db_manager.initialize_db()

    # Fetch and print current blocks
    blocks = await db_manager.get_current_blocks()
    G = {"tag": "fuuuuuuuuu", "command": "transform"}
    B = []
    for block in blocks:
        new_block = block.content
        for transformation in ["html2md"]:
            new_block = apply_transformation(transformation, new_block)
            print(new_block)
        # if new_block is a string, then append it to the list.  If it is a list, then extend the list
        if isinstance(new_block, str):
            B.append({"content": new_block, "tag": block.tag})
        else:
            B.extend([{"content": b, "tag": block.tag} for b in new_block])
    await db_manager.add_group_with_blocks(G, B)
    # print(json.dumps(B, indent=4))

    # Close the database connection
    await db_manager.close()


if __name__ == "__main__":
    os.chdir("/Users/odewahn/Desktop/cat-essay")
    asyncio.run(main())

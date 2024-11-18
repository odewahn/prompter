import asyncio
import jinja2

# Add the ../src directory to the path
import sys
import os

sys.path.append(os.path.abspath("../src"))

# Import code from the src directory
from db import DatabaseManager
from constants import DEFAULT_DB_URL
from transformations import apply_transformation
from db import Group, Block


fn_pattern = "{{group_tagZ}}-{{block_tag.split('.')[0]}}-{{'%03d' % position}}.md"


async def main():
    # Initialize the database manager with a sample database URL
    db_manager = DatabaseManager(DEFAULT_DB_URL)

    # Initialize the database (create tables if they don't exist)
    await db_manager.initialize_db()

    # Fetch and print current blocks
    blocks, headers = await db_manager.get_current_blocks()
    template = jinja2.Template(fn_pattern, undefined=jinja2.StrictUndefined)
    for block in blocks:
        try:
            fn = jinja2.Template(fn_pattern, undefined=jinja2.StrictUndefined).render(
                **block
            )
            print(fn)
        except jinja2.exceptions.UndefinedError as e:
            print(f"Error: {e}")
            print(f"Valid jinja variables are: {headers}")
            print(f"You entered: {fn_pattern}")
            break
    await db_manager.close()


if __name__ == "__main__":
    asyncio.run(main())

# For pyinstaller, we want to show something as quickly as possible
print("Initializing handlers...")
from rich.console import Console

console = Console()

# Set up a loading message as the libraries are loaded
with console.status(f"[bold green]Loading required libraries...") as status:
    from db import DatabaseManager, Block
    from ebooklib import epub
    from ebooklib import ITEM_DOCUMENT as ebooklib_ITEM_DOCUMENT
    import os
    import warnings
    import sys
    import glob
    import uuid
    from rich import print
    from constants import *
    from transformations import apply_transformation
    import json
    from rich.table import Table
    from sqlalchemy.inspection import inspect

db_manager = None
current_db_url = None

# ignore future warnings
warnings.filterwarnings("ignore", category=FutureWarning)


def init_db_manager(db_url):
    global db_manager, business
    db_manager = DatabaseManager(db_url)
    current_db_url = db_url


class ExitREPLException(Exception):
    pass


# ******************************************************************************


async def handle_command(args, command):
    command_handlers = {
        "use": handle_use_command,
        "load": handle_load_command,
        "exit": handle_exit_command,
        "version": handle_version_command,
        "transform": handle_transform_command,
        "blocks": handle_blocks_command,
        "cd": handle_cd_command,
        "ls": handle_ls_command,
    }
    handler = command_handlers.get(args.command)
    if handler:
        await handler(args, command)
    else:
        print(f"Unknown command: {args.command}")


# ******************************************************************************
# Utility functions
# ******************************************************************************
def args_to_kwargs(args):
    kwargs = {}
    for arg in vars(args):
        kwargs[arg] = getattr(args, arg)
    return kwargs


def generate_random_tag():
    # Return a random identifier in the format "ABC-123"
    # The goal is for the identifier to be easy to remember and type
    map = "ABCEFGHXYZ"
    x = str(hash(uuid.uuid1()) % 1000000).zfill(6)
    # Map the first 3 digits to letters
    part_one_mapped_to_letters = "".join(map[int(i)] for i in x[:3])
    return f"{part_one_mapped_to_letters}-{x[3:]}"


# ******************************************************************************
# Functions related to loading files
# ******************************************************************************
async def load_files(files, tag, command):
    group_id = await db_manager.add_group(tag, command)
    for file in files:
        if file.endswith(".epub"):
            await _load_epub(file, group_id)
        else:
            await _load_text_file(file, group_id)


async def _load_epub(file, group_id):
    console.log(f"Loading EPUB file: {file}")
    book = epub.read_epub(file, {"ignore_ncx": True})
    for item in book.get_items():
        if item.get_type() == ebooklib_ITEM_DOCUMENT:
            content = item.get_content().decode("utf-8")
            await db_manager.add_block(group_id, content, item.get_name())


async def _load_text_file(file, group_id):
    console.log(f"Loading text file: {file}")
    with open(file, "r") as f:
        content = f.read()
        await db_manager.add_block(group_id, content, os.path.basename(file))


# ******************************************************************************
# Implementations of the command handlers
# ******************************************************************************


async def handle_use_command(args, command):
    new_db_url = f"sqlite+aiosqlite:///{args.db_name}.db"
    new_db_manager = DatabaseManager(new_db_url)
    await new_db_manager.initialize_db()
    init_db_manager(new_db_url)
    console.log(f"Using database: {args.db_name}.db")


async def handle_load_command(args, command):
    files = []
    for file_pattern in args.files:
        files.extend(glob.glob(file_pattern))
    tag = args.tag or generate_random_tag()
    await load_files(files, tag, command)


async def handle_exit_command(args, command):
    print("Exiting...")
    await db_manager.close()
    raise ExitREPLException()


async def handle_version_command(args, command):
    print(f"Version: {VERSION}")


async def handle_transform_command(args, command):
    blocks = await db_manager.get_current_blocks()
    G = {"tag": args.tag, "command": command}
    B = []
    try:
        for block in blocks:
            new_block = block.content
            for transformation in args.transformation:
                new_block = apply_transformation(
                    transformation, new_block, **args_to_kwargs(args)
                )
            # if new_block is a string, then append it to the list.  If it is a list, then extend the list
            if isinstance(new_block, str):
                B.append({"content": new_block, "tag": block.tag})
            else:
                B.extend([{"content": b, "tag": block.tag} for b in new_block])
        await db_manager.add_group_with_blocks(G, B)
    except Exception as e:
        print(f"[red]{e}")


async def handle_blocks_command(args, command):

    print(args)
    try:
        blocks, column_names = await db_manager.get_current_blocks(args.where)
    except Exception as e:
        print(f"[red]{e}")
        return

    # Specify the columns to display
    display_columns = ["group_tag", "block_id", "block_tag", "content", "token_count"]

    table = Table(title="Current Blocks")

    # Add columns to the table using introspected column names
    for column_name in display_columns:
        table.add_column(column_name, style="magenta")

    for block in blocks:
        # Create a row with the block's attributes
        row = [str(getattr(block, column_name)) for column_name in display_columns]
        # Replace newlines in content preview
        # Adjust content preview to handle newlines and limit length
        if "content" in display_columns:
            content_index = display_columns.index("content")
            row[content_index] = row[content_index][:40].replace("\n", " ") + (
                "..." if len(row[content_index]) > 40 else ""
            )
        table.add_row(*row)

    console.print(table)
    console.print(f"Total blocks: {len(blocks)}")
    console.print(f"Column names: {column_names}")


async def handle_cd_command(args, command):
    path = os.path.expanduser(args.path)
    try:
        os.chdir(path)
        console.log(f"Changed directory to: {os.getcwd()}")
    except Exception as e:
        console.log(f"[red]Failed to change directory: {e}[/red]")


async def handle_ls_command(args, command):
    try:
        import os
        import pwd
        import grp
        import stat
        from datetime import datetime

        entries = os.listdir(".")
        console.print("Files and directories in the current directory:")
        # Define fixed widths for each column
        col_widths = {
            "permissions": 10,
            "n_links": 3,
            "owner": 8,
            "group": 8,
            "size": 10,
            "mtime": 16,
            "entry_type": 2,
            "entry": 20,
        }

        for entry in entries:
            entry_stat = os.stat(entry)
            permissions = stat.filemode(entry_stat.st_mode)
            n_links = entry_stat.st_nlink
            owner = pwd.getpwuid(entry_stat.st_uid).pw_name
            group = grp.getgrgid(entry_stat.st_gid).gr_name
            size = entry_stat.st_size
            mtime = datetime.fromtimestamp(entry_stat.st_mtime).strftime("%Y-%m-%d %H:%M")
            entry_type = "📁" if os.path.isdir(entry) else "📄"
            console.print(
                f"{permissions:<{col_widths['permissions']}} "
                f"{n_links:<{col_widths['n_links']}} "
                f"{owner:<{col_widths['owner']}} "
                f"{group:<{col_widths['group']}} "
                f"{size:<{col_widths['size']}} "
                f"{mtime:<{col_widths['mtime']}} "
                f"{entry_type:<{col_widths['entry_type']}} "
                f"{entry:<{col_widths['entry']}}"
            )
    except Exception as e:
        console.log(f"[red]Failed to list directories: {e}[/red]")

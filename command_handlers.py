# For pyinstaller, we want to show something as quickly as possible
print("Initializing handlers...")
from rich.console import Console

console = Console()

# Set up a loading message as the libraries are loaded
with console.status(f"[bold green]Loading required libraries...") as status:
    from db import DatabaseManager
    from ebooklib import epub
    from ebooklib import ITEM_DOCUMENT as ebooklib_ITEM_DOCUMENT
    import os
    import warnings
    import glob
    import uuid
    from rich import print
    from constants import *
    from transformations import apply_transformation
    from rich.table import Table
    import aiohttp
    from jinja2 import Template
    from shlex import split as shlex_split
    from command_parser import create_parser


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
        "run": handle_run_command,
    }
    handler = command_handlers.get(args.command)
    if handler:
        await handler(args, command)
    else:
        raise Exception(f"Unknown command: {args.command}")


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


async def load_file_or_url(fn):
    if fn.startswith("http"):
        # Use aiohttp to download the file
        async with aiohttp.ClientSession() as session:
            async with session.get(fn) as response:
                if response.status == 200:
                    return await response.text()
                else:
                    raise Exception(
                        f"Failed to download file: {fn} ({response.status})"
                    )
    else:
        try:
            with open(os.path.expanduser(fn), "r") as f:
                return f.read()
        except Exception as e:
            raise Exception(f"Failed to load file: {fn} because {e}")


# ******************************************************************************
# Functions related to loading files
# ******************************************************************************
async def load_files(files, tag, command):
    if not files:
        raise Exception("File(s) not found.")
    group_id = await db_manager.add_group(tag, command)
    for file in files:
        # If the text file does not exist then throw an error
        if not os.path.exists(file):
            raise Exception(f"File os.path.exists(file)not found: {file}")
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
    # Read the content of the file and add it as a block
    with open(file, "r") as f:
        content = f.read()
        await db_manager.add_block(group_id, content, os.path.basename(file))


# ******************************************************************************
# Functions related to running a series of commands from a file
# ******************************************************************************


async def interpret(fn, metadata={"block": "THIS IS THE BLOCK"}):
    # Load the file
    try:
        content = await load_file_or_url(fn)
    except Exception as e:
        print(f"[red]{e}")
        return
    # Parse the content into instructions
    print("Raw content:\n", content)
    #
    template = Template(content)
    instructions = template.render(**metadata)
    # Remove any blank lines from the instructions and return as a list
    commands = [line for line in instructions.split("\n") if line.strip()]
    # process each command
    parser = create_parser()
    for command in commands:
        print(command)
        # Skip comments
        if command.startswith("#"):
            continue
        try:
            args = parser.parse_args(shlex_split(command))
            await handle_command(args, command)
        except SystemExit:
            raise Exception("Invalid command. Halting execution.")


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
    try:
        await load_files(files, tag, command)
        console.log(f"Loaded {len(files)} files into group {tag}")
    except Exception as e:
        print(f"[red]{e}")
        raise


async def handle_exit_command(args, command):
    print("Exiting...")
    await db_manager.close()
    raise ExitREPLException()


async def handle_version_command(args, command):
    print(f"Version: {VERSION}")


async def handle_transform_command(args, command):
    try:
        blocks, column_names = await db_manager.get_current_blocks(args.where)
    except Exception as e:
        print(f"[red]{e}")
        return

    G = {"tag": args.tag if args.tag else generate_random_tag(), "command": command}
    B = []
    try:
        for block in blocks:
            new_block = block["content"]
            for transformation in args.transformation:
                new_block = apply_transformation(
                    transformation, new_block, **args_to_kwargs(args)
                )
            # if new_block is a string, then append it to the list.  If it is a list, then extend the list
            if isinstance(new_block, str):
                B.append({"content": new_block, "tag": block["block_tag"]})
            else:
                B.extend([{"content": b, "tag": block["block_tag"]} for b in new_block])
        await db_manager.add_group_with_blocks(G, B)
        console.log(f"New group {G['tag']} created with {len(B)} blocks.")
    except Exception as e:
        print(f"[red]{e}")
        raise


async def handle_blocks_command(args, command):
    display_columns = ["group_tag", "block_id", "block_tag", "content", "token_count"]

    try:
        blocks, column_names = await db_manager.get_current_blocks(args.where)
    except Exception as e:
        print(f"[red]{e}")
        raise

    table = Table(title="Current Blocks")

    # Add columns to the table using column names we want to display
    for c in display_columns:
        table.add_column(c, style="magenta")

    # Add rows to the table
    for block in blocks:
        row = []
        for c in display_columns:
            if c == "content":
                row.append(block[c][:40].replace("\n", " ") + "...")  # Truncate content
            else:
                row.append(str(block[c]))

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
        raise


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
            mtime = datetime.fromtimestamp(entry_stat.st_mtime).strftime(
                "%Y-%m-%d %H:%M"
            )
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


async def handle_run_command(args, command):
    console.log(f"Running file: {args.fn}")
    try:
        await interpret(args.fn)
    except Exception as e:
        console.print(f"[red]{e}[/red]")

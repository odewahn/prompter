# For pyinstaller, we want to show something as quickly as possible
print("Initializing handlers...")
from rich.console import Console

console = Console()

# Set up a loading message as the libraries are loaded
with console.status(f"[bold green]Loading required libraries...") as status:
    from src.db import DatabaseManager
    from src.constants import *
    from src.transformations import apply_transformation
    from src.openai_functions import complete
    from src.speak import dump_to_audio
    from src.common import *
    from src.command_parser import create_parser
    from src.shared_environment import shared_environment as env
    from src.common import command_split
    from src.render_templates import *
    from src.embeddings import create_embedder, compute_embeddings
    from ebooklib import epub
    from ebooklib import ITEM_DOCUMENT as ebooklib_ITEM_DOCUMENT
    import os
    import warnings
    import glob
    from rich import print
    from rich.table import Table
    from jinja2 import Template, StrictUndefined
    import itertools
    import webbrowser
    import yaml
    import traceback
    import urllib.parse
    import json


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
# Utility functions
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
        "pwd": handle_pwd_command,
        "run": handle_run_command,
        "complete": handle_complete_command,
        "groups": handle_groups_command,
        "checkout": handle_set_group,
        "squash": handle_squash_command,
        "write": handle_write_command,
        "speak": handle_speak_command,
        "browse": handle_browse_command,
        "help": handle_help_command,
        "history": handle_history_command,
        "env": handle_env_command,
        "set": handle_set_command,
        "unset": handle_unset_command,
        "select": handle_select_command,
        "retag": handle_retag_command,
        "embed": handle_embed_command,
        "export": handle_export_command,
    }
    handler = command_handlers.get(args.command)
    if handler:
        await handler(args, command)
    else:
        raise Exception(f"Unknown command: {args.command}")


# ******************************************************************************
# Utilitity functions specific to commands
# ******************************************************************************
def find_prev_and_next(l):
    # if there are no element then raise an exception
    if len(l) == 0:
        raise Exception("No groups found")
    # First check if there is only one element in the list.  If so, then return the same element
    if len(l) == 1:
        return l[0]["group_tag"], l[0]["group_tag"]
    # If there are more than one elements, then find the current group
    current_idx = -1
    # Find the index for the current group
    for index, d in enumerate(l):
        if d.get("is_current") == 1:
            current_idx = index
            break
    # If the current group is not found, then raise an exception
    if current_idx == -1:
        raise Exception("Current group not found")
    # Find the previous and next group tag
    if current_idx == 0:
        # If the current group is the first group, then the previous group is the same as the current group
        prev = l[current_idx]["group_tag"]
        next = l[current_idx + 1]["group_tag"]
    elif current_idx == len(l) - 1:
        # If the current group is the last group, then the next group is the same as the current group
        prev = l[current_idx - 1]["group_tag"]
        next = l[current_idx]["group_tag"]
    else:
        # If the current group is in the middle, then the previous group is the one before the current group
        prev = l[current_idx - 1]["group_tag"]
        next = l[current_idx + 1]["group_tag"]
    return prev, next


def get_tag(tag):
    if tag in ["latest", "first", "next", "previous"]:
        raise Exception(f"{tag} is a reserved word and cannot be used as a tag")
    return tag if tag else generate_random_tag()


# ******************************************************************************
# Functions related to loading files
# ******************************************************************************
async def load_files(files, tag, command):
    print(f"Loading files: {files}")
    if not files:
        raise Exception(f"File(s) not found")
    group_id = await db_manager.add_group(tag, command)
    for file in files:
        # Determine if the file is a URL or a local file
        if file.startswith("http"):
            await _load_url(file, group_id)
        else:
            # If the text file does not exist then throw an error
            file = os.path.expanduser(file)  # Expand ~ to the user's home directory
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


async def _load_url(url, group_id):
    # Read the content of the file and add it as a block
    content = await load_file_or_url(url)
    await db_manager.add_block(group_id, content, url)


# ******************************************************************************
# Functions related to running a series of commands from a file
# ******************************************************************************


async def interpret(fn, preview=False):
    # Load the file
    try:
        content = await load_file_or_url(fn)
    except Exception as e:
        print(f"[red]The following error occurred: {e}")
        print(traceback.format_exc())
        return

    instructions = render_file_or_instruction(content)
    # Remove any blank lines from the instructions and return as a list
    commands = [line for line in instructions.split("\n") if line.strip()]
    # Test if we're just previewing.  If so, then print the commands and return
    if preview:
        print("Commands to be run:")
        for command in commands:
            print(command)
        return
    # process each command
    parser = create_parser()
    for command in commands:
        print(command)
        # Skip comments
        if command.startswith("#"):
            continue
        command = urllib.parse.unquote(command)  # Decode the command
        args = parser.parse_args(command_split(command))
        try:
            await handle_command(args, command)
        except Exception as e:
            print(f"[red]Command:\n    {command}\nreturned the error \n   {e}[/red]")
            print(f"[red]Halting execution of {fn}[/red]")
            break


# ******************************************************************************
# Implementations of the command handlers
# ******************************************************************************
async def set_db(db_name):
    new_db_url = f"sqlite+aiosqlite:///{db_name}"
    new_db_manager = DatabaseManager(new_db_url)
    await new_db_manager.initialize_db()
    init_db_manager(new_db_url)
    console.log(f"Using database: {db_name}")


async def handle_use_command(args, command):
    await set_db(args.db_name)


async def handle_load_command(args, command):
    files = []
    # Add local files to the list
    for file_pattern in [os.path.expanduser(f) for f in args.files]:
        files.extend(glob.glob(file_pattern))
    # Add URLs to the list
    for file in args.files:
        if file.startswith("http"):
            files.append(file)
    tag = get_tag(args.tag)
    # Sort the files
    files.sort()
    await load_files(files, tag, command)
    console.log(f"Loaded {len(files)} files into group {tag}")


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
        print(f"[red]handle_transform_command: {e}")
        return

    G = {"tag": get_tag(args.tag), "command": command}
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
        print(f"[red]handle_transform_command:{e}")


def print_blocks(blocks, column_names, display_columns, title="Current Blocks"):

    table = Table(title=title)

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


async def handle_select_command(args, command):
    if env.get("DEBUG") == "true":
        print(f"Arguments: {args}")
    try:
        where_clause = " ".join(args.where_clause)
        blocks, column_names = await db_manager.get_current_blocks(where_clause)
        G = {"tag": get_tag(args.tag), "command": command}
        B = []
        for block in blocks:
            B.append({"content": block["content"], "tag": block["block_tag"]})
        if not args.preview:
            await db_manager.add_group_with_blocks(G, B)
        else:
            display_columns = [
                "tag",
                "content",
            ]
            print_blocks(B, column_names, display_columns, "Preview of Selected Blocks")
            print(
                "[green]This is a preview.  To confirm the selection, rerun the command with --confirm[/green]"
            )
    except Exception as e:
        print(f"[red]handle_select_command: {e}")
        return


async def handle_retag_command(args, command):
    pattern = " ".join(args.block_tag)
    try:
        blocks, column_names = await db_manager.get_current_blocks("1=1")
        G = {"tag": get_tag(args.tag), "command": command}
        B = []
        RETAG = []
        for block in blocks:
            block_tag = block["block_tag"]
            if args.block_tag:
                block_tag = render_argument(pattern, block=block)
            B.append({"content": block["content"], "tag": block_tag})
            RETAG.append(
                {
                    "old_block_tag": block["block_tag"],
                    "new_block_tag": block_tag,
                    "content": block["content"][:100],
                }
            )
        if not args.preview:
            await db_manager.add_group_with_blocks(G, B)
        else:
            display_columns = [
                "old_block_tag",
                "new_block_tag",
                "content",
            ]
            print_blocks(
                RETAG, display_columns, display_columns, "Preview of Retagged Blocks"
            )
            print(
                "[red]This is a preview.  To confirm the retagging, rerun the command with --confirm[/red]"
            )
    except Exception as e:
        print(f"[red]handle_retag_command: {e.message}")
        print(f"Valid jinja variables are: {column_names}")
        print(f"You entered: {pattern}")
        return


async def handle_blocks_command(args, command):
    try:
        blocks, column_names = await db_manager.get_current_blocks(args.where)
        display_columns = [
            "group_tag",
            "block_id",
            "block_tag",
            "content",
            "position",
            "token_count",
        ]
        print_blocks(blocks, column_names, display_columns)
    except Exception as e:
        print(f"[red]handle_blocks_command: {e}")
        return


async def handle_groups_command(args, command):

    try:
        groups, column_names = await db_manager.get_groups()
    except Exception as e:
        print(f"[red]handle_groups_command: {e}")
        return

    table = Table(title="Groups")

    # Add columns to the table using column names we want to display
    for c in column_names:
        table.add_column(c, style="magenta")

    # Add rows to the table
    for block in groups:
        row = []
        for c in column_names:
            row.append(str(block[c]))
        table.add_row(*row)

    console.print(table)
    console.print(f"Total groups: {len(groups)}")


async def handle_cd_command(args, command):
    path = os.path.expanduser(args.path)
    try:
        os.chdir(path)
        console.log(f"Changed directory to: {os.getcwd()}")
        db_name = db_manager.current_db_url.split("/")[
            -1
        ]  # get the current database name
        print("Current db:", db_manager.current_db_url)
        await set_db(db_name)  # use the database in the new directory
    except Exception as e:
        console.log(f"[red]Failed to change directory: {e}[/red]")


# Add a handle_pwd_command
async def handle_pwd_command(args, command):
    try:
        console.log(f"Current directory: {os.getcwd()}")
    except Exception as e:
        console.log(f"[red]Failed to get current directory: {e}[/red]")


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
        await interpret(args.fn, args.preview)
    except Exception as e:
        console.print(f"[red]handle_run_command: {e.message}[/red]")


async def handle_complete_command(args, command):
    if not args.task:
        raise Exception("You must supply the filename or URL of a task to complete")
    # load the templates
    task_text = None
    persona_text = None
    context = {}
    try:
        task_text = await load_file_or_url(args.task)
        if args.persona:
            persona_text = await load_file_or_url(args.persona)
        if args.context:
            context = await load_context(args.context)
    except Exception as e:
        raise e
    # Get the current blocks
    current_blocks, _ = await db_manager.get_current_blocks(args.where)
    if not current_blocks:
        raise Exception("No blocks found to complete")

    try:
        completed_blocks = await complete(
            current_blocks,
            task_text,
            persona_text,
            context,
            model=args.model,
            temperature=args.temperature,
        )
        # Add the completed blocks to the database
        G = {
            "tag": get_tag(args.tag),
            "command": command,
            "task_prompt": task_text,
            "persona_prompt": persona_text,
            "context_yaml": yaml.dump(context),
        }
        B = []
        for block in completed_blocks:
            B.append({"content": block["completion"], "tag": block["block_tag"]})
        await db_manager.add_group_with_blocks(G, B)
        console.log(f"New group {G['tag']} created with {len(B)} blocks.")
    except Exception as e:
        raise Exception(f"Error completing blocks: {e}")


async def handle_set_group(args, command):
    try:
        tag = args.tag
        groups, column_headers = await db_manager.get_groups()
        # Find the index of the current group
        previous_tag, next_tag = find_prev_and_next(groups)
        if args.tag == "latest":
            tag = groups[-1]["group_tag"]
        elif args.tag == "first":
            tag = groups[0]["group_tag"]
        elif args.tag == "next":
            tag = next_tag
        elif args.tag == "previous":
            tag = previous_tag
        await db_manager.set_current_group(tag)
    except Exception as e:
        raise Exception(f"Error setting group: {e}")


async def handle_squash_command(args, command):
    try:
        blocks, headers = await db_manager.get_squashed_current_blocks(args.delimiter)
        # Add the completed blocks to the database
        G = {
            "tag": get_tag(args.tag),
            "command": command,
        }
        B = []
        for block in blocks:
            B.append({"content": block["content"], "tag": block["block_tag"]})
        await db_manager.add_group_with_blocks(G, B)
        console.log(f"New group {G['tag']} created with {len(B)} blocks.")
    except Exception as e:
        raise Exception(f"Error squashing blocks: {e}")


# write --fn="test-{{block_tag.split('.')[0]}}-{{ '%04d' % position}}.txt" --where="block_id = 146"
async def handle_write_command(args, command):
    try:
        blocks, column_names = await db_manager.get_current_blocks(args.where)
    except Exception as e:
        print(f"[red]handle_write_command: {e}")
        return

    for block in blocks:
        try:
            fn = render_argument(args.fn, block=block)
            with open(fn, "w") as f:
                print(f"Writing to {fn}")
                f.write(block["content"])
        except Exception as e:
            print(f"[red]Error: {e}")
            print(f"Valid jinja variables are: {column_names}")
            print(f"You entered: {args.fn}")
            break


async def handle_squash_command(args, command):
    try:
        blocks, column_names = await db_manager.get_current_blocks(args.where)
        G = {
            "tag": get_tag(args.tag),
            "command": command,
        }
        B = []
        # Use itertools to pull out groups based o the block_tag
        for tag, group in itertools.groupby(blocks, key=lambda x: x["block_tag"]):
            # join all the content in the block_group
            out = args.delimiter.join([block["content"] for block in group])
            B.append({"content": out, "tag": tag})
        await db_manager.add_group_with_blocks(G, B)
        console.log(f"New group {G['tag']} created with {len(B)} blocks.")

    except Exception as e:
        print(f"[red]handle_squash_command: {e}")
        return


async def handle_speak_command(args, command):
    try:
        blocks, column_names = await db_manager.get_current_blocks(args.where)
    except Exception as e:
        print(f"[red]handle_speak_command: {e}")
        return
    # Convert the blocks to audio
    for block in blocks:
        try:
            fn = render_argument(args.fn, block=block)
            if not args.preview:
                with console.status(
                    f"[bold green]Converting {fn} to audio: {block['content'][:20]}"
                ) as status:
                    await dump_to_audio(block["content"], fn, args.voice, args.speed)
        except Exception as e:
            print(f"[red]Error: {e}")
            print(f"Valid jinja variables are: {column_names}")
            print(f"You entered: {args.fn}")
            break


async def handle_browse_command(args, command):
    url = PROD_WEB_URL if env.get("env") == "prod" else DEV_WEB_URL
    try:
        webbrowser.open(url)
    except Exception as e:
        print(f"[red]handle_browse_command: {e}")
        return


async def handle_help_command(args, command):
    parser = create_parser()
    parser.print_help()


async def handle_history_command(args, command):
    try:
        groups, _ = await db_manager.get_groups()
        for group in groups:
            print(urllib.parse.unquote(group["command"]))
    except Exception as e:
        print(f"[red]Error fetching command history: {e}[/red]")


async def handle_env_command(args, command):
    for key, value in env.get_all().items():
        print(f"[green]{key}[/green] = [cyan]{value}[/cyan]")


async def handle_set_command(args, command):
    env[args.key] = args.value


async def handle_unset_command(args, command):
    env.unset(args.key)


async def handle_embed_command(args, command):

    current_blocks, _ = await db_manager.get_current_blocks(args.where)
    if not current_blocks:
        raise Exception("No blocks found to complete")
    try:
        with console.status(f"[bold green]Embedding...") as status:
            embedder = create_embedder(args.embedder)
            embeddings = await compute_embeddings(
                [block["content"] for block in current_blocks], embedder
            )
        # Write out to a csv file
        with open(args.fn, "w") as f:
            # Write a header row
            f.write(
                "group_tag, block_tag, block_id, position, "
                + ", ".join([f"v{i}" for i in range(len(embeddings[0]))])
                + "\n",
            )
            for block, embedding in zip(current_blocks, embeddings):
                f.write(
                    f"{block['group_tag']}, {block['block_tag']}, {block['block_id']}, {block['position']}, {','.join(map(str, embedding))}\n"
                )

    except Exception as e:
        raise Exception(f"Error embedding blocks: {e}")


async def handle_export_command(args, command):
    try:
        blocks, column_names = await db_manager.get_current_blocks()
        with open(args.fn, "w") as f:
            f.write(json.dumps(blocks, indent=4))

    except Exception as e:
        print(f"[red]handle_export_command: {e}")
        return

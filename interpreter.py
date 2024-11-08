# For pyinstaller, we want to show something as quickly as possible
print("Starting Interpreter...")
from rich.console import Console

console = Console()

# Set up a loading message as the libraries are loaded
with console.status(f"[bold green]Loading required libraries...") as status:
    import asyncio
    from rich import print
    from command_parser import create_parser
    from command_handlers import handle_command, ExitREPLException
    from constants import *
    from shlex import split as shlex_split


async def interpret(fn):
    console.log(f"Interpreting {fn}...")
    return

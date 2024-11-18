# For pyinstaller, we want to show something as quickly as possible
print("Starting Interpreter...")
from rich.console import Console

console = Console()

# Set up a loading message as the libraries are loaded
with console.status(f"[bold green]Loading required libraries...") as status:
    from src.command_parser import create_parser
    from src.command_handlers import handle_command, ExitREPLException
    from src.constants import *
    import asyncio
    from rich import print
    from shlex import split as shlex_split


async def interpret(fn):
    console.log(f"Interpreting {fn}...")
    return

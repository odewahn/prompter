# For pyinstaller, we want to show something as quickly as possible
print("Starting REPL...")
from rich.console import Console

console = Console()

# Set up a loading message as the libraries are loaded
with console.status(f"[bold green]Loading required libraries...") as status:
    import asyncio
    from rich import print
    from prompt_toolkit import PromptSession
    from command_parser import create_parser
    from command_handlers import handle_command, ExitREPLException
    from art import text2art
    from constants import *
    import os
    from shlex import split as shlex_split


async def interactive_repl():
    session = PromptSession()
    parser = create_parser()
    Art = text2art("prompter")
    print(f"[green]{Art}")
    print(f"Prompter version {VERSION}")
    # is os.environ["OPENAI_API_KEY"] is not set then print a warning
    if "OPENAI_API_KEY" not in os.environ:
        print(OPENAI_KEY_NOT_SET)

    while True:
        try:
            command = await session.prompt_async("prompter> ")
            try:
                args = parser.parse_args(shlex_split(command))
                await handle_command(args, command)
            except SystemExit:
                print("Invalid command or arguments.")
        except (EOFError, KeyboardInterrupt):
            break  # Exit the loop on Ctrl-C or Ctrl-D
        except ExitREPLException:
            raise  # Propagate the exception to stop the REPL

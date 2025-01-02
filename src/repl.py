# For pyinstaller, we want to show something as quickly as possible
print("Starting REPL...")
from rich.console import Console

console = Console()

# Set up a loading message as the libraries are loaded
with console.status(f"[bold green]Loading required libraries...") as status:
    from src.command_parser import create_parser
    from src.command_handlers import handle_command, ExitREPLException
    from src.constants import *
    from src.shared_environment import shared_environment as env
    import asyncio
    from rich import print
    from prompt_toolkit import PromptSession
    import os
    from shlex import split as shlex_split
    from argparse import ArgumentError
    from art import text2art
    from jinja2 import Environment, BaseLoader, DebugUndefined


async def interactive_repl():
    session = PromptSession()
    parser = create_parser()
    Art = text2art("prompter")
    print(f"[green]{Art}")
    print(f"Prompter version {VERSION}")
    # is os.environ["OPENAI_API_KEY"] is not set then print a warning
    if "OPENAI_API_KEY" not in os.environ:
        print(MESSAGE_OPENAI_KEY_NOT_SET)

    while True:
        try:
            command = await session.prompt_async("prompter> ")
            # Run the command through the jinja template engine
            rtemplate = Environment(
                loader=BaseLoader, undefined=DebugUndefined
            ).from_string(command)
            interpreted_command = rtemplate.render(env.get_all())
            if env.get("DEBUG") == "true":
                print(f"[green]Interpreted command: {interpreted_command}")
            args = parser.parse_args(shlex_split(interpreted_command))
            await handle_command(args, interpreted_command)
        except ArgumentError as e:
            print("Invalid command", e)
        except ExitREPLException:
            raise
        except (EOFError, KeyboardInterrupt):
            break  # Exit the loop on Ctrl-C or Ctrl-D
        except Exception as e:
            console.log(
                f"[red]Command:\n    {command}\nreturned the error \n   {e}[/red]"
            )

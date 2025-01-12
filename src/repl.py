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
    from src.common import command_split
    from src.render_templates import *
    import asyncio
    from rich import print
    from prompt_toolkit import PromptSession
    import os
    from argparse import ArgumentError
    from art import text2art
    from jinja2 import Template, StrictUndefined, UndefinedError
    import json


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
            # If the command is empty, skip it
            if not command:
                continue
            # Run the command through the jinja template engine
            interpreted_command = render_file_or_instruction(command)
            args = parser.parse_args(command_split(interpreted_command))
            await handle_command(args, interpreted_command)
        except ArgumentError as e:
            print("Invalid command", e)
        except ExitREPLException:
            raise
        except (EOFError, KeyboardInterrupt):
            break  # Exit the loop on Ctrl-C or Ctrl-D
        except InvalidTemplate as e:
            print(f"[red]interactive_repl: {e}[/red]\n")
            print("Try:\n")
            print("* checking that you've quoted string correctly")
            print("* checking that you've used single ticks inside double ticks")
            print(f"* wrapping block-level variables with [green]<%raw%>...<%endraw%>")
            print(
                f"* checking that any environment variables exist in \n[green]{json.dumps(env.get_all(),indent=2)}[/green]"
            )
        except Exception as e:
            console.log(
                f"[red]Command:\n    {command}\nreturned the error \n   {e}[/red]"
            )
            if env.get("DEBUG") == "true":
                console.print_exception()

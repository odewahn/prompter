import asyncio
from prompt_toolkit import PromptSession
from prompt_toolkit.patch_stdout import patch_stdout
from repl_parser import create_parser
from repl_handlers import handle_command, ExitREPLException


async def interactive_repl():
    session = PromptSession()
    parser = create_parser()

    with patch_stdout():
        while True:
            try:
                command_input = await session.prompt_async("Enter command: ")
                try:
                    args = parser.parse_args(command_input.split())
                    await handle_command(args)
                except SystemExit:
                    print("Invalid command or arguments.")
            except (EOFError, KeyboardInterrupt):
                break  # Exit the loop on Ctrl-C or Ctrl-D
            except ExitREPLException:
                raise  # Propagate the exception to stop the REPL

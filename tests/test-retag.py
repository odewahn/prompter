import argparse
import sys

# append the path of the
# parent directory
sys.path.append("..")

from src.command_parser import create_parser
from prompt_toolkit import PromptSession
from src.common import command_split

parser = create_parser()
session = PromptSession()


# Make a simple repl that will read and parse commands
# from the user and print them out

while True:
    try:
        command = session.prompt("prompter> ")
        # Use shlex to split the command into a list of arguments
        # This is necessary because the argparse parser expects
        # a list of arguments, not a string
        # Split the command while preserving quotes
        # Split the command into the command name and its arguments
        command_parts = command_split(command)
        print(f"Command parts: {command_parts}")
        args = parser.parse_args(command_parts)
        print(f"args: {args}")
        # print(f"args.block_tag: {args.block_tag}")
        # print(f"Result: {' '.join(args.block_tag)}")
    except argparse.ArgumentError as e:
        print("Invalid command", e)
    except Exception as e:
        print("Error", e)
        break


# retag tag like '%ch%'

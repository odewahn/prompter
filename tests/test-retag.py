import argparse
import sys

# append the path of the
# parent directory
sys.path.append("..")

from src.command_parser import create_parser
from shlex import split as shlex_split
from jinja2 import Template, StrictUndefined
from prompt_toolkit import PromptSession

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
        args = parser.parse_args([command])
        print(" ".join(args.block_tag))
    except argparse.ArgumentError as e:
        print("Invalid command", e)
    except Exception as e:
        print("Error", e)
        break

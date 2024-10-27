# For pyinstaller, we want to show something as quickly as possible
print("Initializing parser...")
from rich.console import Console

console = Console()

# Set up a loading message as the libraries are loaded
with console.status(f"[bold green]Loading required libraries...") as status:
    import argparse


def create_parser():
    parser = argparse.ArgumentParser(description="Prompter repl")

    parser.add_argument("--tag", help="Tag to use for the group", required=False)

    subparsers = parser.add_subparsers(dest="command")

    def add_subparser(name, help_text, arguments):
        subparser = subparsers.add_parser(name, help=help_text)
        for arg, kwargs in arguments:
            subparser.add_argument(arg, **kwargs)
        return subparser

    add_subparser("use", "Use a new database", [
        ("db_name", {"type": str, "help": "Database name to use"})
    ])

    add_subparser("load", "Load files into a BlockGroup", [
        ("files", {"nargs": "+", "help": "List of files to load"})
    ])

    add_subparser("version", "Print the version", [])

    add_subparser("exit", "Exit the repl", [])

    add_subparser("transform", "Transform a block", [
        ("transformation", {"nargs": "+", "help": "Transformations to apply"}),
        ("--N", {"type": int, "help": "Number of tokens to split", "required": False})
    ])

    add_subparser("blocks", "List all blocks", [])

    return parser

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
    parser.add_argument(
        "--where", help="Where clause for the query", required=False, type=str
    )

    subparsers = parser.add_subparsers(dest="command")

    def add_subparser(name, help_text, arguments):
        subparser = subparsers.add_parser(name, help=help_text)
        for arg, kwargs in arguments:
            subparser.add_argument(arg, **kwargs)
        return subparser

    add_subparser(
        "use",
        "Use a new database",
        [("db_name", {"type": str, "help": "Database name to use"})],
    )

    add_subparser(
        "load",
        "Load a file or files as a new group",
        [
            ("files", {"nargs": "+", "help": "List of files to load"}),
            ("--tag", {"help": "Tag to use for the group", "required": False}),
        ],
    )

    add_subparser("version", "Print the version", [])

    add_subparser("exit", "Exit the repl", [])

    add_subparser(
        "transform",
        "Transform a block",
        [
            ("transformation", {"nargs": "+", "help": "Transformations to apply"}),
            ("--tag", {"help": "Tag to use for the group", "required": False}),
            (
                "--where",
                {"help": "Where clause for the blocks", "required": False, "type": str},
            ),
            (
                "--N",
                {
                    "type": int,
                    "help": "Number of tokens to split",
                    "required": False,
                    "default": 1000,
                },
            ),
        ],
    )

    add_subparser(
        "blocks",
        "List all blocks",
        [
            (
                "--where",
                {"help": "Where clause for the blocks", "required": False, "type": str},
            ),
        ],
    )

    add_subparser(
        "cd",
        "Change the working directory",
        [
            ("path", {"type": str, "help": "Path to change to"}),
        ],
    )

    add_subparser("ls", "List directories in the current directory", [])

    return parser

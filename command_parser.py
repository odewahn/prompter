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

    # Use the main parser for each subparser that requires the --tag option
    use_parser = subparsers.add_parser("use", help="Use a new database")
    use_parser.add_argument("db_name", type=str, help="Database name to use")

    load_parser = subparsers.add_parser("load", help="Load files into a BlockGroup")
    load_parser.add_argument("files", nargs="+", help="List of files to load")

    version_parser = subparsers.add_parser("version", help="Print the version")

    exit_parser = subparsers.add_parser("exit", help="Exit the repl")

    transform_parser = subparsers.add_parser("transform", help="Transform a block")
    transform_parser.add_argument(
        "transformation", nargs="+", help="Transformations to apply"
    )
    transform_parser.add_argument(
        "--N", type=int, help="Number of tokens to split", required=False
    )

    blocks_parser = subparsers.add_parser("blocks", help="List all blocks")

    # Adding a command to create a new database
    use_parser = subparsers.add_parser("use", help="Use a new database")
    use_parser.add_argument("db_name", type=str, help="Database name to use")

    # Adding a command to load files into a Group
    load_parser = subparsers.add_parser("load", help="Load files into a BlockGroup")
    load_parser.add_argument("files", nargs="+", help="List of files to load")

    # Adding command to print the version
    version_parser = subparsers.add_parser("version", help="Print the version")

    # Adding a command to exit the repl
    exit_parser = subparsers.add_parser("exit", help="Exit the repl")

    # Adding a command to transform a block
    transform_parser = subparsers.add_parser("transform", help="Transform a block")
    transform_parser.add_argument(
        "transformation", nargs="+", help="Transformations to apply"
    )

    transform_parser.add_argument(
        "--N", type=int, help="Number of tokens to split", required=False
    )

    # Adding a command to list all blocks
    blocks_parser = subparsers.add_parser("blocks", help="List all blocks")

    return parser

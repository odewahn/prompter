# For pyinstaller, we want to show something as quickly as possible
print("Initializing parser...")
from rich.console import Console

console = Console()

# Set up a loading message as the libraries are loaded
with console.status(f"[bold green]Loading required libraries...") as status:
    from src.constants import *
    import argparse


class ArgumentParserError(Exception):
    pass


# This class is used to throw an exception when an error occurs
# in the argument parser. It is used to prevent the program from
# exiting when an error occurs in the argument parser.
class ThrowingArgumentParser(argparse.ArgumentParser):

    def exit(self, status=0, message=None):
        if message:
            raise ArgumentParserError(message)

    def error(self, message):
        raise ArgumentParserError(message)


def create_parser():
    parser = ThrowingArgumentParser(exit_on_error=False)

    parser.add_argument("--tag", help="Tag to use for the group", required=False)
    parser.add_argument(
        "--where", help="Where clause for the query", required=False, type=str
    )

    subparsers = parser.add_subparsers(dest="command")

    def add_subparser(name, help_text, arguments, subparsers=subparsers):
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

    add_subparser(
        "select",
        "Select a block by supplying a where clause and an argument",
        [
            (
                "where_clause",
                {
                    "type": str,
                    "nargs": "+",
                    "help": "Where clause for the query",
                },
            ),
            ("--tag", {"help": "Tag to use for the group", "required": False}),
            ("--confirm", {"help": "Confirm the selection", "action": "store_true"}),
        ],
    )

    # "blocks-{%raw%}{{position}}{%endraw%}.txt"
    add_subparser(
        "retag",
        "Retag current blocks by supplying a jinja template (remember to use <%raw%>)",
        [
            (
                "block_tag",
                {
                    "nargs": "+",
                    "help": "Jinja template to rewrite block tag (use <%raw%>)",
                },
            ),
            ("--tag", {"help": "Tag for the new group", "required": False}),
            (
                "--confirm",
                {
                    "help": "Confirm the new tags and save to the database",
                    "action": "store_true",
                },
            ),
        ],
    )

    add_subparser("version", "Print the version", [])

    add_subparser("exit", "Exit the repl", [])

    add_subparser("history", "Print the command history", [])

    add_subparser("help", "Print help text", [])

    add_subparser("browse", "Open the data browser", [])

    add_subparser("env", "Print environment variables", [])

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
                "--n",
                {
                    "type": int,
                    "help": "Number of tokens to split",
                    "required": False,
                    "default": 1000,
                },
            ),
            (
                "--overlap",
                {
                    "type": int,
                    "help": "Percentage of overlap for the window",
                    "required": False,
                    "default": 10,
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
        "groups",
        "List all groups",
        [
            (
                "--where",
                {"help": "Where clause for the group", "required": False, "type": str},
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

    add_subparser("pwd", "Print the current directory", [])

    add_subparser(
        "run",
        "Run a file",
        [
            ("fn", {"type": str, "help": "File or URL to run"}),
            (
                "--preview",
                {
                    "help": "Preview the output",
                    "action": "store_true",
                    "default": False,
                },
            ),
        ],
    )

    add_subparser(
        "complete",
        "Complete a block using openai",
        [
            ("task", {"help": "Filename of the task template"}),
            ("--tag", {"help": "Tag to use for the group", "required": False}),
            (
                "--persona",
                {"help": "Filename of the persona template", "required": False},
            ),
            (
                "--metadata",
                {
                    "help": "Metadata file",
                    "default": DEFAULT_METADATA_FN,
                },
            ),
            (
                "--model",
                {
                    "help": "Model to use",
                    "default": OPENAI_DEFAULT_MODEL,
                },
            ),
            (
                "--temperature",
                {
                    "type": float,
                    "help": "Temperature to use",
                    "default": OPENAI_DEFAULT_TEMPERATURE,
                },
            ),
            (
                "--where",
                {"help": "Where clause for the blocks", "required": False, "type": str},
            ),
            (
                "--source",
                {
                    "help": "URL or local path for the task or scenario (does not apply to metadata)",
                    "required": False,
                    "type": str,
                },
            ),
        ],
    )

    add = add_subparser(
        "checkout",
        "Checkout a group",
        [
            ("tag", {"help": "Tag to use for the group"}),
        ],
    )

    add = add_subparser(
        "squash",
        "Squash the current group into a new group by tag",
        [
            ("--delimiter", {"help": "Delimiter to use", "default": "\n"}),
            ("--tag", {"help": "Tag for the new group", "required": False}),
        ],
    )

    add = add_subparser(
        "write",
        "Write the current group to a file",
        [
            (
                "--fn",
                {
                    "type": str,
                    "help": "Filename pattern (jinja2) to write to",
                    "default": "{{block_tag}}",
                },
            ),
            (
                "--where",
                {"help": "Where clause for the blocks", "required": False, "type": str},
            ),
        ],
    )

    add = add_subparser(
        "speak",
        "Convert the current block to audio files",
        [
            (
                "--fn",
                {
                    "type": str,
                    "help": "Filename pattern (jinja2) to write to",
                    "default": "{{block_tag.split('.') | first}}-{{ '%04d' % position}}.mp3",
                },
            ),
            (
                "--where",
                {"help": "Where clause for the blocks", "required": False, "type": str},
            ),
            (
                "--voice",
                {"help": "Voice to use", "default": "alloy"},
            ),
            (
                "--preview",
                {"help": "Preview the filenames", "action": "store_true"},
            ),
        ],
    )

    add = add_subparser(
        "set",
        "Set an environment variable",
        [
            ("key", {"type": str, "help": "Key to set"}),
            ("value", {"type": str, "help": "Value to set"}),
        ],
    )

    add = add_subparser(
        "unset",
        "Remove an environment variable",
        [
            ("key", {"type": str, "help": "Key to set"}),
        ],
    )

    return parser

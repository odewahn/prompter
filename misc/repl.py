import argparse
from rich.prompt import Prompt
from rich.console import Console
from rich import print
from prompt_toolkit import PromptSession
import shlex
from art import text2art


ACTIONS = [
    "init",
    "load",
    "transform",
    "filter",
    "groups",
    "blocks",
    "dump",
    "prompt",
    "prompts",
    "prompt-log",
    "transfer-prompts",
    "set-group",
    "version",
    "set-api-key",
    "merge-prompts-into-block",
]
TRANSFORMATIONS = [
    "token-split",
    "clean-epub",
    "html-h1-split",
    "html-h2-split",
    "html2md",
    "html2txt",
    "new-line-split",
    "sentence-split",
]


def define_arguments(argString=None):

    parser = argparse.ArgumentParser(
        description="Mangage prommpts across long blocks of text", exit_on_error=False
    )
    parser.add_argument(
        "action",
        choices=ACTIONS,
        help="The action to perform ",
    )

    # Universal arguments
    parser.add_argument(
        "--db", help="The database file", required=False, default="prompter.db"
    )
    # Arguments related to loading files
    parser.add_argument("--fn", help="Filename", required=False)
    # Arguments related to naming or fetching blocks, prompts, etc.
    parser.add_argument("--group_tag", help="Tag to filter on", required=False)
    parser.add_argument("--prompt_tag", help="Tag to filter on", required=False)
    parser.add_argument("--where", help="SQLITE where clause", required=False)
    # Arguments related to prompting
    parser.add_argument("--prompt", help="Prompt to use", required=False)
    parser.add_argument("--model", help="Model to use", required=False, default="gpt-4")
    parser.add_argument(
        "--fake",
        help="Generate fake prompt response data",
        required=False,
        default=False,
        action=argparse.BooleanOptionalAction,
    )
    # Arguments related to transformation operations
    parser.add_argument(
        "--transformation",
        help=f"Transformation to use ({','.join(TRANSFORMATIONS)})",
        required=False,
    )
    # Arguments related to tranferring data from prompts to metadata or blocks
    parser.add_argument(
        "--to",
        help="Where to transfer prompts",
        choices=["metadata", "blocks"],
        required=False,
        default="metadata",
    )
    # Arguments related to tranferring data from prompts to metadata or blocks
    parser.add_argument(
        "--source",
        help="Source to dump from",
        choices=["blocks", "prompts"],
        required=False,
        default="blocks",
    )
    # Arguments related to metadata
    parser.add_argument(
        "--globals", help="Name of the file with global metadata", required=False
    )
    parser.add_argument(
        "--metadata_key",
        help="Name of metadata key; this will match the name in a prompt template",
        required=False,
    )
    # Arguments related to dumping data
    parser.add_argument(
        "--delimiter",
        help="Delimiter to use when dumping prompts",
        required=False,
        default="\n\n",
    )

    if argString:
        return parser.parse_args(shlex.split(argString))
    else:
        return parser.parse_args()


version = "0.0.1"

Art = text2art("prompter")
print(f"[green]{Art}")
# print(f"v{version}\n")

# Create prompt object.
session = PromptSession()

if __name__ == "__main__":
    while True:
        argString = session.prompt("prompter> ")
        if argString == "exit":
            break
        try:
            with define_arguments(argString) as args:
                print(args)
        except Exception as e:
            print(e)

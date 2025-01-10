import argparse
import sys

# append the path of the
# parent directory
sys.path.append("..")

from src.render_templates import *
from src.command_parser import create_parser
from prompt_toolkit import PromptSession
from src.common import command_split


# load in the sample command file
s = open("../data/env-test.prompter").read()

# render the file
try:
    file = render(
        s, metadata={"SOURCE": "http://example.com", "DEST": "~/Desktop/odewahn"}
    )
    print(file)
except InvalidTemplate as e:
    print(e.message)


def parse_arg_test(command):
    parser = create_parser()
    command_parts = command_split(command)
    print(f"Command parts: {command_parts}")
    return parser.parse_args(command_parts)


args = parse_arg_test(
    """
write --fn="~/test-{{block_tag.split('.')[0]}}-{{ '%04d' % position}}.txt" --where="block_id = 146"
"""
)
out = render_argument(
    args.fn,
    block={"block_tag": "test.123", "position": 1},
    metadata={"title": "A simple plan", "author": "Andrew Odewahn"},
)
print("The answer is", out)


args = parse_arg_test(
    """
load http//example.com ~/Desktop/odewahn/cat-essay.txt test.epub
"""
)

out = render_argument(
    args.files,
    block={"block_tag": "test.123", "position": 1},
    metadata={"title": "A simple plan", "author": "Andrew Odewahn"},
)
print("The answer is", out)

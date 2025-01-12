print("Initializing handlers...")
from rich.console import Console

console = Console()

# Set up a loading message as the libraries are loaded
with console.status(f"[bold green]Loading required libraries...") as status:
    from src.constants import *
    from src.common import *
    from src.shared_environment import shared_environment as env
    from jinja2 import Template, StrictUndefined, UndefinedError
    from jinja2 import Environment, BaseLoader, DebugUndefined
    import json
    import os

ERROR_MSG = """
Unable to process the template because of the following error:

[red]{0}[/red]

You can try:

* Wrapping undefined variables in {{%raw%}} and {{%endraw%}} tags
* Checking any that quotes and tics are used correctly

`set DEBUG true` and run the command for more info
"""


class InvalidTemplate(Exception):
    def __init__(self, message):
        self.message = ERROR_MSG.format(message)


def pretty_log(header, obj):
    console.log(f"\n[magenta]{header}[/magenta]\n[green]{obj}[/green]\n")


# Ignore comments in the file
def remove_comments(s):
    return "\n".join(
        [line for line in s.split("\n") if not line.strip().startswith("#")]
    )


# Merge the kwargs with the shared environment at the top level.  For example, if the shared environment is
# {"ENV": "dev"} and the kwargs are {"metadata": {"SOURCE": "http://example.com"}}, the merged dictionary should be
# {"ENV": "dev", "SOURCE": "http://example.com"}
def merge_kwargs(**kwargs):
    # Merge the shared environment with the kwargs
    if env.get("DEBUG") == "true":
        console.log(f"[cyan]Merging kwargs with shared environment")
        pretty_log("Environment keys", env.get_all().keys())
        pretty_log("Kwargs keys", kwargs.keys())
    # Set the shared environment as the base
    merged = {**env.get_all()}
    for key, value in kwargs.items():
        # raise an error if the value if not a dictionary
        if not isinstance(value, dict):
            raise TypeError(f"{key} argument must be a dictionary")
        merged = {**merged, **value}
    if env.get("DEBUG") == "true":
        pretty_log("Merged keys", merged.keys())
    return merged


# Render and individual file or instruction.  A lot of this is
# boilerplate around how to centralize arguments, print deub log, and handle errors
# Note that we're permisive here around missing variables
def render_file_or_instruction(content, **kwargs):
    if env.get("DEBUG") == "true":
        console.log(f"[cyan]Rendering a file")
    content = remove_comments(content)
    try:
        merged_kwargs = merge_kwargs(**kwargs)
        template = Environment(loader=BaseLoader, undefined=DebugUndefined).from_string(
            content
        )
        if env.get("DEBUG") == "true":
            pretty_log("Original", content)
        res = template.render(merged_kwargs)
        if env.get("DEBUG") == "true":
            pretty_log("Rendered", res)
        return res
    except Exception as e:
        raise InvalidTemplate(e.message)


def render_string_argument(arg, merged_kwargs):
    try:
        if env.get("DEBUG") == "true":
            console.log(f"\n[green]Original: {arg}\n")
        if not arg.startswith("http"):
            arg = os.path.expanduser(arg)
        # Use the strict undefined to raise an error if a variable is missing
        template = Template(arg, undefined=StrictUndefined)
        res = template.render(merged_kwargs)
        if env.get("DEBUG") == "true":
            console.log(f"\n[cyan]Rendered: {res}\n")
        return res
    except UndefinedError as e:
        raise InvalidTemplate(e.message)


def render_list_argument(arg, merged_kwargs):
    try:
        if env.get("DEBUG") == "true":
            console.log(f"\n[green]Original: {arg}\n")
        res = []
        for a in arg:
            res.append(render_string_argument(a, merged_kwargs))
        return res
    except UndefinedError as e:
        raise InvalidTemplate(e.message)


# An argument *cannot* have missing variables
def render_argument(arg, **kwargs):
    if env.get("DEBUG") == "true":
        console.log(f"[cyan]Rendering an argument")
    merged_kwargs = merge_kwargs(**kwargs)
    # if the type of the arg is a string then use the single string function
    if isinstance(arg, str):
        return render_string_argument(arg, merged_kwargs)
    elif isinstance(arg, list):
        return render_list_argument(arg, merged_kwargs)
    else:
        raise TypeError("Argument must be a string or a list")

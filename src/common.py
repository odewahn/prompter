# For pyinstaller, we want to show something as quickly as possible
print("Initializing common...")
from rich.console import Console

console = Console()

# Set up a loading message as the libraries are loaded
with console.status(f"[bold green]Loading required libraries...") as status:
    from src.constants import *
    import os
    import uuid
    from rich import print
    import aiohttp
    import yaml
    import shlex


# ******************************************************************************
# Utility functions
# ******************************************************************************
def args_to_kwargs(args):
    kwargs = {}
    for arg in vars(args):
        kwargs[arg] = getattr(args, arg)
    return kwargs


def generate_random_tag():
    # Return a random identifier in the format "ABC-123"
    # The goal is for the identifier to be easy to remember and type
    map = "abcdefgxyz"
    x = str(hash(uuid.uuid1()) % 1000000).zfill(6)
    # Map the first 3 digits to letters
    part_one_mapped_to_letters = "".join(map[int(i)] for i in x[:3])
    return f"{part_one_mapped_to_letters}-{x[3:]}"


async def load_file_or_url(fn):
    if fn.startswith("http"):
        # Use aiohttp to download the file
        async with aiohttp.ClientSession() as session:
            async with session.get(fn) as response:
                if response.status == 200:
                    return await response.text()
                else:
                    raise Exception(
                        f"Failed to download file: {fn} ({response.status})"
                    )
    else:
        try:
            with open(os.path.expanduser(fn), "r") as f:
                return f.read()
        except Exception as e:
            raise Exception(f"Failed to load file: {fn} because {e}")


async def load_metadata(fn):
    try:
        with open(os.path.expanduser(fn), "r") as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        return {}
    except Exception as e:
        raise Exception(f"Failed to load metadata file: {fn} because {e}")


# Centralizing this here for now, but I might want to revisit this later using a better lexing process
# https://stackoverflow.com/questions/6868382/python-shlex-split-ignore-single-quotes
def command_split(value):
    return shlex.split(value)

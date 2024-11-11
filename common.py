# For pyinstaller, we want to show something as quickly as possible
print("Initializing common...")
from rich.console import Console

console = Console()

# Set up a loading message as the libraries are loaded
with console.status(f"[bold green]Loading required libraries...") as status:
    import os
    import uuid
    from rich import print
    from constants import *
    import aiohttp
    import yaml


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
    map = "ABCEFGHXYZ"
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

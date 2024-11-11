# For pyinstaller, we want to show something as quickly as possible
print("Initializing handlers...")
from rich.console import Console

console = Console()

# Set up a loading message as the libraries are loaded
with console.status(f"[bold green]Loading required libraries...") as status:
    from constants import *
    import os
    import yaml
    import asyncio
    from openai import AsyncOpenAI
    import openai
    from common import load_file_or_url


async def openai_completion(client, data, task_text, persona_text, model, temperature):
    response = await client.chat.completions.create(
        model=model,
        messages=[
            {"role": "user", "content": task_text},
            {"role": "system", "content": persona_text},
        ],
        temperature=temperature,
    )
    response_txt = str(response.choices[0].message.content)
    return {**data, "completion": response_txt}


async def complete(
    blocks,
    task_fn,
    persona_fn=None,
    metadata_fn=None,
    model=OPENAI_DEFAULT_MODEL,
    temperature=OPENAI_DEFAULT_TEMPERATURE,
):
    # is os.environ["OPENAI_API_KEY"] is not set then print a warning
    if "OPENAI_API_KEY" not in os.environ:
        raise Exception(MESSAGE_OPENAI_KEY_NOT_SET)

    # Now we're ready to go!
    print("Requesting completions from OpenAI")
    print("Number of blocks:", len(blocks))
    print("task_fn:", task_fn)
    print("persona_fn:", persona_fn)
    print("metadata_fn:", metadata_fn)
    print("model:", model)
    print("Temperature:", temperature)

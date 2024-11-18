# For pyinstaller, we want to show something as quickly as possible
print("Initializing handlers...")
from rich.console import Console

console = Console()

# Set up a loading message as the libraries are loaded
with console.status(f"[bold green]Loading required libraries...") as status:
    from src.constants import *
    from src.db import DatabaseManager
    from src.common import load_file_or_url, load_metadata
    import os
    import asyncio
    from openai import AsyncOpenAI
    import jinja2


async def openai_completion(
    client, block, task_template, persona_template, metadata, model, temperature
):
    block.update(metadata)  # merge the metadata with the block
    task = task_template.render(**block)
    messages = [
        {"role": "user", "content": task},
    ]
    if persona_template:
        persona = persona_template.render(**block)
        messages.append({"role": "system", "content": persona})

    response = await client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
    )
    response_txt = str(response.choices[0].message.content)
    return {**block, "completion": response_txt}


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

    # Load the task and persona text
    task_text = None
    persona_text = None
    metadata = {}
    try:
        task_text = await load_file_or_url(task_fn)
        if persona_fn:
            persona_text = await load_file_or_url(persona_fn)
        if metadata_fn:
            metadata = await load_metadata(metadata_fn)
    except Exception as e:
        raise e

    # Set up jinja templates based on the task and persona text
    task_template = jinja2.Template(task_text)
    persona_template = None
    if persona_text:
        persona_template = jinja2.Template(persona_text)

    client = AsyncOpenAI(api_key=os.environ["OPENAI_API_KEY"])
    # Create a list of requests to send to the OpenAI API
    requests = [
        openai_completion(
            client,
            block,
            task_template,
            persona_template,
            metadata,
            model,
            temperature,
        )
        for block in blocks
    ]

    # Send the requests to the OpenAI API
    with console.status(
        f"[bold green]Completing {len(requests)} blocks using {model}..."
    ) as status:
        results = await asyncio.gather(*requests)

    return results

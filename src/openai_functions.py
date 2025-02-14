# For pyinstaller, we want to show something as quickly as possible
print("Initializing handlers...")
from rich.console import Console

console = Console()

# Set up a loading message as the libraries are loaded
with console.status(f"[bold green]Loading required libraries...") as status:
    from src.constants import *
    from src.render_templates import *
    import os
    import asyncio
    from openai import AsyncOpenAI


async def openai_completion(
    client, block, task_text, persona_text, context, model, temperature
):
    task = render_file_or_instruction(task_text, context=context, block=block)

    messages = [
        {"role": "user", "content": task},
    ]
    if persona_text:
        persona = render_file_or_instruction(persona_text, context=context, block=block)
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
    task_text=None,
    persona_text=None,
    context={},
    model=OPENAI_DEFAULT_MODEL,
    temperature=OPENAI_DEFAULT_TEMPERATURE,
):

    # is os.environ["OPENAI_API_KEY"] is not set then print a warning
    if "OPENAI_API_KEY" not in os.environ:
        raise Exception(MESSAGE_OPENAI_KEY_NOT_SET)

    client = AsyncOpenAI(api_key=os.environ["OPENAI_API_KEY"])
    # Create a list of requests to send to the OpenAI API
    requests = [
        openai_completion(
            client,
            block,
            task_text,
            persona_text,
            context,
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

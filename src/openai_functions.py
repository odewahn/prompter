# For pyinstaller, we want to show something as quickly as possible
print("Initializing handlers...")
from rich.console import Console

console = Console()

# Set up a loading message as the libraries are loaded
with console.status(f"[bold green]Loading required libraries...") as status:
    from src.constants import *
    from src.db import DatabaseManager
    from src.common import load_file_or_url, load_metadata
    from src.render_templates import *
    import os
    import asyncio
    from openai import AsyncOpenAI
    import jinja2
    from pydub import AudioSegment
    import json


async def openai_completion(
    client, block, task_text, persona_text, metadata, model, temperature
):
    task = render_file_or_instruction(task_text, metadata=metadata, block=block)

    messages = [
        {"role": "user", "content": task},
    ]
    if persona_text:
        persona = render_file_or_instruction(
            persona_text, metadata=metadata, block=block
        )
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
    metadata={},
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


# **************************************************************************************************
# Audio related code
# **************************************************************************************************


async def speak(client, text, fn, voice="alloy"):
    stream = await client.audio.speech.create(model="tts-1", voice=voice, input=text)
    await stream.astream_to_file(fn)


# https://developers.deepgram.com/docs/text-chunking-for-tts-optimization
def chunk_text(text, chunk_size=MAX_SPEECH_LENGTH):
    chunks = []
    words = text.split()
    current_chunk = ""
    for word in words:
        if len(current_chunk) + len(word) <= chunk_size:
            current_chunk += " " + word
        else:
            chunks.append(current_chunk.strip())
            current_chunk = word
    if current_chunk:
        chunks.append(current_chunk.strip())
    return chunks


async def dump_to_audio(text, fn, voice):
    # is os.environ["OPENAI_API_KEY"] is not set then print a warning
    if "OPENAI_API_KEY" not in os.environ:
        raise Exception(MESSAGE_OPENAI_KEY_NOT_SET)

    # Save the current working directory so that we can return to it

    client = AsyncOpenAI(api_key=os.environ["OPENAI_API_KEY"])
    chunks = chunk_text(text)
    chunk_audio_name = [f".tmp-{fn}-{idx}.mp3" for idx in range(len(chunks))]
    requests = [
        speak(client, chunk, chunk_audio_name[idx], voice)
        for idx, chunk in enumerate(chunks)
    ]
    await asyncio.gather(*requests)
    # Reassemble the chunks.  If there is only one chunk, just rename it
    # Otherwise, concatenate the chunks and save the result
    if len(chunk_audio_name) == 1:
        os.rename(chunk_audio_name[0], fn)
        return
    else:
        audio = AudioSegment.empty()
        for chunk_name in chunk_audio_name:
            audio += AudioSegment.from_mp3(chunk_name)
        audio.export(f"{fn}", format="mp3")
        # Clean up
        for chunk_name in chunk_audio_name:
            os.remove(chunk_name)

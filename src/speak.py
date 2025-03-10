# For pyinstaller, we want to show something as quickly as possible
print("Initializing handlers...")
from rich.console import Console

console = Console()

# Set up a loading message as the libraries are loaded
with console.status(f"[bold green]Loading required libraries...") as status:
    from src.constants import *
    import os
    import asyncio
    from openai import AsyncOpenAI
    from pydub import AudioSegment

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


async def dump_to_audio(text, fn, voice, speed=1.0):
    # is os.environ["OPENAI_API_KEY"] is not set then print a warning
    if "OPENAI_API_KEY" not in os.environ:
        raise Exception(MESSAGE_OPENAI_KEY_NOT_SET)

    # Save the current working directory so that we can return to it
    console.log(f"Dumping text to audio: {fn} using voice: {voice} at speed: {speed}")

    client = AsyncOpenAI(api_key=os.environ["OPENAI_API_KEY"])
    chunks = chunk_text(text)
    chunk_audio_name = [f".tmp-{fn}-{idx}.mp3" for idx in range(len(chunks))]
    requests = [
        speak(client, chunk, chunk_audio_name[idx], voice)
        for idx, chunk in enumerate(chunks)
    ]
    await asyncio.gather(*requests)
    # Concatenate the chunks and save the result
    audio = AudioSegment.empty()
    for chunk_name in chunk_audio_name:
        audio += AudioSegment.from_mp3(chunk_name)
    # Export the audio with FFmpeg, using the atempo filter for time-stretching with pitch preservation
    audio.export(
        f"{fn}",
        format="mp3",  # Output format (you can customize it as needed)
        parameters=[
            "-filter:a",
            f"atempo={speed}",  # FFmpeg atempo filter for speed adjustments
        ],
    )

    # Clean up
    for chunk_name in chunk_audio_name:
        os.remove(chunk_name)

from pathlib import Path
from openai import AsyncOpenAI
import os
import yaml
import warnings
import sys
import asyncio
from pydub import AudioSegment

sys.path.append("../../")
from completions_common import load_config

ENV_FILENAME = ".prompter"

MAX_SPEECH_LENGTH = 4096


config = load_config()


client = AsyncOpenAI(api_key=config["openai"])


TXT = """
Today, we're going to talk about O'Reilly's AI Use Policy for Employees. This policy is designed to help us harness the power of generative AI technologies while 
mitigating risks like data security vulnerabilities, privacy concerns, and intellectual 
property issues.
"""


async def speak(text, fn, voice="alloy"):
    print(f"Speaking: {text[:20]}...")
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


async def speak_long(text, fn, voice="alloy"):
    chunks = chunk_text(text)
    chunck_audio_name = [f"tmp-{fn}-{idx}.mp3" for idx in range(len(chunks))]
    print(chunks)
    requests = [
        speak(chunk, chunck_audio_name[idx], voice) for idx, chunk in enumerate(chunks)
    ]
    await asyncio.gather(*requests)
    # Reassemble the chunks
    audio = AudioSegment.empty()
    for chunk_name in chunck_audio_name:
        print(f"Appending {chunk_name}")
        audio += AudioSegment.from_mp3(chunk_name)
    audio.export(f"{fn}.mp3", format="mp3")
    # Clean up
    for chunk_name in chunck_audio_name:
        os.remove(chunk_name)


async def main():
    await speak_long(TXT, "test", "alloy")


if __name__ == "__main__":
    asyncio.run(main())

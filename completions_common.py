from rich.console import Console

from pathlib import Path
import os
from dotenv import load_dotenv
import yaml
from prompt_toolkit import PromptSession
import asyncio
from openai import AsyncOpenAI
from groq import AsyncGroq
import openai
from groq import Groq
from pydub import AudioSegment


ENV_FILENAME = ".prompter"

console = Console()

MAX_SPEECH_LENGTH = 2048


# model looks like this: "openai:gpt-4o" or "groq:llama-3"
def parse_model(model):
    model_components = model.split(":")
    if len(model_components) == 1:
        provider = "openai"
        model = model
    else:
        provider = model_components[0]
        model = model_components[1]
    return provider, model


# Load the config file
def load_config():
    home = str(Path.home())
    # Test if the file exists
    if not os.path.isfile(home + "/" + ENV_FILENAME):
        return {}
    # Load the file
    with open(home + "/" + ENV_FILENAME, "r") as f:
        config = yaml.safe_load(f)
    return config


def save_config(config):
    home = str(Path.home())
    with open(home + "/" + ENV_FILENAME, "w") as f:
        yaml.dump(config, f)
    console.log(f"API key set successfully and saved in {home}/{ENV_FILENAME}")
    return


# Write the API key to the .prompter file in the home directory
async def action_set_api_key():
    session = PromptSession()
    # get the config
    config = load_config() or {}
    # get the provider and API key
    provider = await session.prompt_async("Provider (openai | groq)> ")
    api_key = await session.prompt_async(f"API key > ")
    print("You entered: ", provider, api_key)
    # write the key to the config
    config[provider] = api_key
    # save the config
    save_config(config)


# Check if the .prompter file exists in the home directory
def load_env():
    home = str(Path.home())
    if not os.path.isfile(home + "/" + ENV_FILENAME):
        return False
    load_dotenv(home + "/" + ENV_FILENAME)
    console.log(f"Loaded API key from {home}/{ENV_FILENAME}")
    return True


def action_models(args):
    if args.provider == "openai":
        return openai_models(args)
    elif args.provider == "groq":
        return groq_models(args)
    return "Unknown provider"


async def complete(args, tasks, persona_text=None):
    provider, model = parse_model(args.model)
    # Load the config file
    config = load_config()
    # Check if the API key is set
    if provider not in config:
        raise Exception(
            f"You must set an API key for {provider} to use the {model}. Run the auth command to set it."
        )
    # Perform the correct call
    if provider == "openai":
        client = AsyncOpenAI(api_key=config["openai"])
        requests = [
            openai_completion(args, client, persona_text, task) for task in tasks
        ]
        print(f"Requesting {len(requests)} completions from OpenAI")
        results = await asyncio.gather(*requests)
        return results
    elif provider == "groq":
        client = AsyncGroq(api_key=config["groq"])
        requests = [groq_completion(args, client, persona_text, task) for task in tasks]
        print(f"Requesting {len(requests)} completions from Groq")
        results = await asyncio.gather(*requests)
        return results
        # return groq_completion(args, config, text, persona_text)

    return "Unknown provider"


# **************************************************************************************************
# OpenAI related code
# **************************************************************************************************

# from completions_common import parse_model, load_config


async def openai_completion(args, client, persona_text=None, task={}):
    _, model = parse_model(args.model)
    response = await client.chat.completions.create(
        model=args.model,
        messages=[
            {"role": "user", "content": task["prompt_text"]},
            {"role": "system", "content": persona_text},
        ],
        temperature=0.1,
    )
    response_txt = str(response.choices[0].message.content)
    return {**task, "prompt_response": response_txt}


def openai_models(args):
    # Load the config file
    config = load_config()
    # Check if the API key is set
    openai.api_key = config["openai"]
    models = openai.Model.list()
    out = [model.id for model in models.data]
    return sorted(out)


# **************************************************************************************************
# Groq related code
# **************************************************************************************************


async def groq_completion(args, client, persona_text=None, task={}):
    _, model = parse_model(args.model)
    response = await client.chat.completions.create(
        model=model,
        messages=[
            {"role": "user", "content": task["prompt_text"]},
            {"role": "system", "content": persona_text},
        ],
        temperature=0.1,
    )
    response_txt = str(response.choices[0].message.content)
    return {**task, "prompt_response": response_txt}


def groq_models(args):
    provider, model = parse_model(args.model)
    # Load the config file
    config = load_config()
    # Check if the API key is set
    client = Groq(
        # This is the default and can be omitted
        api_key=config["groq"],
    )

    models = client.models.list()

    out = [model.id for model in models.data]

    return sorted(out)


# **************************************************************************************************
# Audio related code
# **************************************************************************************************


async def speak(client, text, fn, voice="alloy"):
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


async def dump_to_audio(args, text, fn, voice):
    # Save the current working directory so that we can return to it
    cwd = os.getcwd()
    # change to the output directory if one is specified
    if args.dir:
        # expand the direcotry if it includes a ~
        os.chdir(os.path.expanduser(args.dir))
    # Load the config file
    config = load_config()
    client = AsyncOpenAI(api_key=config["openai"])
    chunks = chunk_text(text)
    chunk_audio_name = [f".tmp-{fn}-{idx}.mp3" for idx in range(len(chunks))]
    print(chunks)
    requests = [
        speak(client, chunk, chunk_audio_name[idx], args.voice)
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
    # Return to the original working directory
    os.chdir(cwd)

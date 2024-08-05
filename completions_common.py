from rich.console import Console
from pathlib import Path
import os
from dotenv import load_dotenv
import yaml
from prompt_toolkit import PromptSession
from completions_openai import *
from completions_groq import *


ENV_FILENAME = ".prompter"

console = Console()


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
def action_set_api_key():
    session = PromptSession()
    # get the config
    config = load_config()
    # get the provider and API key
    provider = session.prompt("Provider (openai | groq)> ")
    api_key = session.prompt(f"API key > ")
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


def complete(args, text, persona_text=None):
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
        return openai_completion(args, config, text, persona_text)
    elif provider == "groq":
        return groq_completion(args, config, text, persona_text)

    return "Unknown provider"

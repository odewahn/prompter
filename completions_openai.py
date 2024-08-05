import openai

from completions_common import *


def openai_completion(args, config, text, persona_text=None):
    openai.api_key = config["openai"]
    response = openai.ChatCompletion.create(
        model=args.model,
        messages=[
            {"role": "user", "content": text},
            {"role": "system", "content": persona_text},
        ],
        temperature=0.1,
    )
    response_txt = str(response.choices[0].message.content)
    return response_txt


def openai_models(args):
    # Load the config file
    config = load_config()
    # Check if the API key is set
    openai.api_key = config["openai"]
    models = openai.Model.list()
    out = [model.id for model in models.data]
    return sorted(out)

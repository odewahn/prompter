from groq import Groq
from completions_common import *


def groq_completion(args, config, text, persona_text=None):
    provider, model = parse_model(args.model)
    client = Groq(
        # This is the default and can be omitted
        api_key=config["groq"],
    )

    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": persona_text},
            {
                "role": "user",
                "content": text,
            },
        ],
        model=model,
    )

    return chat_completion.choices[0].message.content


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

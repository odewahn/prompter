import openai

from completions_common import *


async def openai_completion(args, client, persona_text=None, task={}):
    print("openai_completion for task", task["block_id"])
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

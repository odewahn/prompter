import asyncio

import asyncio


# Add the ../src directory to the path
import sys
import os

sys.path.append(os.path.abspath("../src"))


from embeddings import create_embedder, compute_embeddings


async def main():
    texts = ["Hello world", "Another text"]
    openai_embedder = create_embedder("openai", api_key=os.environ["OPENAI_API_KEY"])
    dummy_embedder = create_embedder("dummy", dimensionality=32)

    # Compute embeddings using OpenAI
    openai_embeddings = await compute_embeddings(texts, openai_embedder)
    print("OpenAI Embeddings:", openai_embeddings)

    print("\n********************\n")
    # Compute dummy embeddings
    dummy_embeddings = await compute_embeddings(texts, dummy_embedder)
    print("Dummy Embeddings:", dummy_embeddings)


# Run the example
asyncio.run(main())

from abc import ABC, abstractmethod
from dataclasses import dataclass
import asyncio
import os
from src.constants import *


# Base class for embedding
class Embedder(ABC):
    @abstractmethod
    async def compute_embedding(self, text):
        pass


# This class is here for reference and to give a quick way to do tests
@dataclass
class DummyEmbedder(Embedder):
    dimensionality: int = 8

    async def compute_embedding(self, text):
        return [0.0] * self.dimensionality


@dataclass
class OpenAIEmbedder(Embedder):

    async def compute_embedding(self, text):
        from openai import AsyncOpenAI

        # is os.environ["OPENAI_API_KEY"] is not set then print a warning
        if "OPENAI_API_KEY" not in os.environ:
            raise Exception(MESSAGE_OPENAI_KEY_NOT_SET)

        client = AsyncOpenAI(api_key=os.environ["OPENAI_API_KEY"])
        response = await client.embeddings.create(
            model="text-embedding-ada-002", input=text
        )
        return response.data[0].embedding


# Factory function to create an embedder
def create_embedder(embedder_type, **kwargs):
    if embedder_type == "openai":
        return OpenAIEmbedder(**kwargs)
    elif embedder_type == "dummy":
        return DummyEmbedder(**kwargs)
    else:
        raise ValueError(f"Unknown embedder type: {embedder_type}")


# Function to compute embeddings
async def compute_embeddings(texts, embedder):
    tasks = [embedder.compute_embedding(text) for text in texts]
    return await asyncio.gather(*tasks)

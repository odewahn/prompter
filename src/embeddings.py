from abc import ABC, abstractmethod
from dataclasses import dataclass
import asyncio


# Base class for embedding
class Embedder(ABC):
    def __init__(self, api_key: str):
        self.api_key = api_key

    @abstractmethod
    async def compute_embedding(self, text):
        pass


# This class is here for reference and to give a quick way to do tests
class DummyEmbedder(Embedder):
    def __init__(self, api_key: str, dimensionality: int = 8):
        super().__init__(api_key)
        self.dimensionality = dimensionality

    async def compute_embedding(self, text):
        return [0.0] * self.dimensionality


class OpenAIEmbedder(Embedder):
    def __init__(self, api_key: str):
        super().__init__(api_key)

    async def compute_embedding(self, text):
        from openai import AsyncOpenAI

        client = AsyncOpenAI(api_key=self.api_key)
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

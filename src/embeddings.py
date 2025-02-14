from abc import ABC, abstractmethod
from dataclasses import dataclass
import asyncio


# Base class for embedding
class Embedder(ABC):
    @abstractmethod
    async def compute_embedding(self, text):
        pass


@dataclass
class OpenAIEmbedder(Embedder):
    api_key: str

    async def compute_embedding(self, text):
        from openai import AsyncOpenAI

        client = AsyncOpenAI(api_key=self.api_key)
        response = await client.embeddings.create(
            model="text-embedding-ada-002", input=text
        )
        return response["data"][0]["embedding"]


@dataclass
class HuggingFaceEmbedder(Embedder):
    model_name: str

    async def compute_embedding(self, text):
        from transformers import pipeline

        feature_extractor = pipeline("feature-extraction", model=self.model_name)
        return feature_extractor(text)[0]


# Factory function for creating embedders
def create_embedder(embedder_type, **kwargs):
    if embedder_type == "openai":
        return OpenAIEmbedder(**kwargs)
    elif embedder_type == "huggingface":
        return HuggingFaceEmbedder(**kwargs)
    else:
        raise ValueError(f"Unknown embedder type: {embedder_type}")


# Function to compute embeddings
async def compute_embeddings(texts, embedder):
    tasks = [embedder.compute_embedding(text) for text in texts]
    return await asyncio.gather(*tasks)

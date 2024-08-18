import openai
import os
from logger import logger

class OpenAIEmbeddingModel:
    """An OpenAI Embedding Model class following the Singleton Design Pattern.
    If instantiated, will always return the same reference.
    This ensures only one model is ever loaded into memory.
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(OpenAIEmbeddingModel, cls).__new__(cls)
            openai.api_key = os.getenv("OPENAI_API_KEY")  # Set your OpenAI API key here
        return cls._instance

    def embed_documents(self, inputs: str | list[str]) -> list:
        """Create embeddings from the input using OpenAI's API.

        Args:
            inputs (str | list[str]): The prompt(s) to encode. Can be a single prompt or a list of prompts.

        Returns:
            list: a list of embeddings, where each embedding is a list of floats.
        """

        response = openai.embeddings.create(
            input=inputs,
            model="text-embedding-ada-002"  # Specify the OpenAI model for embeddings
        )
         # If response is an object, use dot notation
        embeddings = response.data[0].embedding

        logger.info("Embedding created successfully")

        return [embeddings]

    def embed_query(self, input_query: str):
        """Embed a single query using the OpenAI embedding model.

        Args:
            input_query (str): The query to be embedded.

        Returns:
            list: A flat list representing the embedding of the query.
        """
        embedded_query = self.embed_documents(input_query)
        return embedded_query[0]

# Run at application startup
openai_model = OpenAIEmbeddingModel()

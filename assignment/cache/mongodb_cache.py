from typing import Optional, Any, List
from langchain_core.documents import Document
from langchain_community.vectorstores import MongoDBAtlasVectorSearch
from vector_store.embedding import OpenAIEmbeddingModel
import os
from logger import logger

class MongoDBSemanticCache:
    def __init__(
        self,
        score_threshold: Optional[float] = None,
    ):
        """
        Initialize the MongoDB Semantic Cache.

        Args:
            score_threshold (float): Minimum score threshold for returning results.
        """
        self.embedding = OpenAIEmbeddingModel()
        self.index_name = os.getenv("MONGODB_CACHE_INDEX_NAME")
        self.vector_store = (
                MongoDBAtlasVectorSearch.from_connection_string(
                    connection_string=os.getenv("MONGODB_CONNECTION_URI"),
                    namespace=os.getenv("MONGODB_DATABASE_NAME") + "." + os.getenv("MONGODB_CACHE_COLLECTION"),
                    embedding=self.embedding,
                    index_name=os.getenv("MONGODB_CACHE_INDEX_NAME"),
                )
            )
        self.score_threshold = score_threshold
        self.LLM = "llm_string"
        self.RETURN_VAL = "response"

    def _embed_text(self, text: str) -> List[float]:
        """Convert text into its corresponding embedding."""
        return self.embedding.embed_query(text)

    def _insert_document(self, user_query: str, llm_string: str, response: Any) -> None:
        """Insert a document into the collection."""
        embedding = self._embed_text(user_query)

        # Create a LangChain Document with metadata
        document = Document(
            page_content=user_query,  # or response depending on what you consider the "content"
            metadata={
                "user_query": user_query,
                "llm_string": llm_string,
                "embedding": embedding,
                "response": response,
            }
        )
        
        self.vector_store.add_documents([document])

    def lookup(self, user_query: str, llm_string: str) -> Optional[Any]:
        """Look up based on user_query and llm_string."""
        if not self.vector_store._collection.count_documents({}):
            logger.info("Collection is empty.")
            return None
        
        logger.info("Saerching semantic cache.")

        # Define the post-filter pipeline if score_threshold is set
        post_filter_pipeline = (
            [{"$match": {"score": {"$gte": self.score_threshold}}}]
            if self.score_threshold
            else None
        )

        # Perform the similarity search
        search_response = self.vector_store.similarity_search_with_score(
            query=user_query,
            k=1,
            post_filter_pipeline=post_filter_pipeline,
        )
        logger.info(f"Search response: {len(search_response)}")
        
        # Process and return the result
        if search_response:
            logger.info(f"Semnatic cache hit for query with score: {search_response[0][1]}.")
            return_val = search_response[0][0].metadata.get(self.RETURN_VAL)
            return return_val
        return None


    def update(self, user_query: str, llm_string: str, response: Any) -> None:
        """Update the cache with a new user_query and return value."""
        self._insert_document(user_query, llm_string, response)

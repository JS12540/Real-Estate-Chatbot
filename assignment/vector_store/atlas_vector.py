from langchain.schema import Document as LCDocument
from langchain_community.vectorstores import MongoDBAtlasVectorSearch
from pymongo.database import Database
from vector_store.db import database
from vector_store.embedding import OpenAIEmbeddingModel
import os
from logger import logger


class AtlasVectorStore:
    vector_store: MongoDBAtlasVectorSearch
    database: Database
    embedding: OpenAIEmbeddingModel
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AtlasVectorStore, cls).__new__(cls)
            cls._instance.database = database
            cls._instance.embedding = OpenAIEmbeddingModel()
            cls._instance.vector_store = (
                MongoDBAtlasVectorSearch.from_connection_string(
                    connection_string=os.getenv("MONGODB_CONNECTION_URI"),
                    namespace=os.getenv("MONGODB_DATABASE_NAME") + "." + os.getenv("MONGODB_COLLECTION"),
                    embedding=cls._instance.embedding,
                    index_name=os.getenv("MONGODB_INDEX_NAME"),
                )
            )
        return cls._instance

    def add_documents(self, docs: list[LCDocument], **kwargs) -> list[str]:
        """Storage and generation of embeddings.

        Args:
            docs (list[LCDocument]): Documents to add to the vectorstore.

        Returns:
            List[str]: List of IDs of the added texts.
        """
        return self.vector_store.add_documents(documents=docs, **kwargs)

    def retrieve(
        self,
        query: str,
        k: int = 5,
        pre_filter: dict = None,
        post_filter_pipeline: dict = None,
        with_score: bool = False,
    ) -> list[LCDocument]:
        """Return MongoDB documents most similar to the given query.

        Args:
            query: Text to look up documents similar to.
            k: (Optional) number of documents to return. Defaults to 4.
            pre_filter: (Optional) dictionary of argument(s) to prefilter document
            fields on.
            post_filter_pipeline: (Optional) Pipeline of MongoDB aggregation stages
            following the vectorSearch stage.
            with_score: (Optional) whether to return the scores along with the documents.

        Returns:
            list[LCDocument]:  List of documents most similar to the query and their scores.
        """
        logger.info(f"Retrieving documents for query: {query}")
        if with_score:
            return self.vector_store.similarity_search_with_score(
                query=query,
                k=k,
                pre_filter=pre_filter,
                post_filter_pipeline=post_filter_pipeline,
            )
        return self.vector_store.similarity_search(
            query=query,
            k=k,
            pre_filter=pre_filter,
            post_filter_pipeline=post_filter_pipeline,
        )


atlas_vector_store_obj = AtlasVectorStore()
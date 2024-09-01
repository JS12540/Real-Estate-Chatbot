from langchain.schema import Document as LangChainDocument
from logger import logger
from vector_store.db_cache import cache
from fuzzywuzzy import fuzz

async def process_document_text( text_metadata: dict
) -> list[LangChainDocument]:
    documents = []

    document = LangChainDocument(
            page_content=text_metadata['text'],
            metadata={
                    "Type": "Property Catalogue",
                    **text_metadata['metadata'],
                },
        )
    documents.append(document)

    logger.info(f"Processed {len(documents)} LangChainDocuments.")
    return documents

async def get_cached_response(query):
    cached_data = cache.find_one({"query": query})
    if cached_data:
        return cached_data["response"]
    return None

async def store_cache(query, response):
    cache.replace_one(
        {"query": query}, 
        {"query": query, "response": response}, 
        upsert=True
    )

async def get_fuzzy_cached_response(query, threshold=85):
    all_cached_data = cache.find()
    best_match = None
    best_score = 0

    for data in all_cached_data:
        cached_query = data["query"]
        score = fuzz.ratio(query, cached_query)
        logger.info(f"Score between {query} and {cached_query}: {score}")
        if score > best_score and score >= threshold:
            logger.info(f"Fuzzy match found with score: {score}")
            best_score = score
            best_match = data["response"]

    if best_match:
        logger.info(f"Fuzzy match found with score: {best_score}")
    return best_match
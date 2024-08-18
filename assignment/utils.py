from langchain.schema import Document as LangChainDocument
from logger import logger

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

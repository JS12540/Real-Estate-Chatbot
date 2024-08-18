from PyPDF2 import PdfReader
from agents.metadata import create_metadata
from utils import process_document_text
from vector_store.atlas_vector import AtlasVectorStore
import asyncio
from logger import logger
import re
from text_splitter import RecursiveCharacterTextSplitter

avs = AtlasVectorStore()

from docx import Document

def extract_text_from_docx(docx_path):
    # Load the DOCX file
    doc = Document(docx_path)
    
    # Extract and combine all text from the DOCX file
    full_text = []
    for para in doc.paragraphs:
        full_text.append(para.text)
    
    # Join the paragraphs with a newline separator and return the result
    return '\n'.join(full_text)



async def extract_pdf_text_with_metadata(pdf_path):
    logger.info(f"Processing PDF: {pdf_path}")
    
    # Load the PDF file
    pdf_reader = PdfReader(pdf_path)
    
    # Loop through each page, extract text, and create metadata
    for i in range(len(pdf_reader.pages)):
        page = pdf_reader.pages[i]
        page_text = page.extract_text()
        
        if page_text is None or page_text.strip() == "":
            logger.info(f"Page {i+1} is empty.")
            continue
        
        # Ensure Unicode errors are handled when printing
        safe_text = page_text.encode('ascii', 'ignore').decode('ascii')
        logger.info(f"Extracted text from page {i+1}: {safe_text}")
        
        # Generate metadata for the extracted text
        metadata = await create_metadata(page_text)
        logger.info(f"Metadata for page {i+1}: {metadata}")
        
        # Store the text and metadata
        pdf_data = {
            "text": page_text,
            "metadata": metadata
        }
    
        logger.info("Processing completed.")
        
        # Process and add documents to vector store
        documents = await process_document_text(pdf_data)
        logger.info(f"Adding {len(documents)} documents to the vector store.")
        avs.add_documents(docs=documents)
        logger.info("Documents added.")


def read_pdf(file_path):
    """Read text from a PDF file."""
    with open(file_path, 'rb') as file:
        reader = PdfReader(file)
        text = ''
        for page_num in range(len(reader.pages)):
            page_text = reader.pages[page_num].extract_text()
            text += page_text
    return text

async def create_recursive_embeddings(file_path):
    pdf_text = read_pdf(file_path)
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
    )
    # Split the text
    chunks = text_splitter.split_text(pdf_text)
    # Dictionary to store text and metadata from each page
    pdf_data = {}
    for chunk in chunks:
        metadata = await create_metadata(chunk)
        logger.info(f"Metadata for chunk: {metadata}")

        # Store the text and metadata
        pdf_data = {
            "text": chunk,
            "metadata": metadata
        }
    
        logger.info("Processing completed.")
        
        # Process and add documents to vector store
        documents = await process_document_text(pdf_data)
        logger.info(f"Adding {len(documents)} documents to the vector store.")
        avs.add_documents(docs=documents)
        logger.info("Documents added.")

async def manual_and_image_text():
    text = """
    Commission slab for the current quarter:	
    Number of deals 	Commission (% of price)
    1	2.50%
    2 to 4	3.00%
    5 & above	3.50%
        
    Extra commission kickers:	
    3 BHK + Study unit	0.50%
    50 qualified customer walk-ins in a month	Bonus of $10,000

    """
    metadata = await create_metadata(text)
    logger.info(f"Metadata for chunk: {metadata}")

        # Store the text and metadata
    pdf_data = {
        "text": text,
        "metadata": metadata
    }
    
    logger.info("Processing completed.")
        
    # Process and add documents to vector store
    documents = await process_document_text(pdf_data)
    logger.info(f"Adding {len(documents)} documents to the vector store.")
    avs.add_documents(docs=documents)
    logger.info("Documents added.")



if __name__ == "__main__":
    file_path = r"Dataset/facade-catalogue-and-specifications.pdf"
    asyncio.run(extract_pdf_text_with_metadata(file_path))
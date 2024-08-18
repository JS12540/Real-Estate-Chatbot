import os
import json
import asyncio
from openai import AsyncClient
import sys
from logger import logger

# Suppress encoding errors globally
sys.stdout.reconfigure(errors='ignore')

meta_data_prompt = """
"Given the following text, generate a concise and descriptive metadata summary that includes key topics, 
relevant entities, the text's purpose, and any important dates or figures mentioned. 
Use only below fields for metadata.
The metadata should be formatted as a JSON object with fields such as 'title', 'keywords', 'entities', 'category'. 
This metadata will be used for efficient retrieval and context augmentation in a RAG system."
Metadata should only contain 4-5 fields no more than that.

Example:

{
    "title": "Real estate data",
    "keywords": ["real estate", "data"],
    "entities": ["Real estate", "Data"],
    "category": "real estate",
}

{
    "title": "Real estate data",
    "keywords": ["real estate", "data"],
    "entities": ["Real estate", "Data"],
    "category": "real estate",
}

""" 

async def create_metadata(text):
    messages = [
        {"role": "system", "content": meta_data_prompt},
        {"role": "user", "content": str(text)},
    ]
    model = os.getenv("OPENAI_MODEL")

    try:
        async_client = AsyncClient(
            api_key=os.environ["OPENAI_API_KEY"],
        )

        # Request a completion from the OpenAI API
        response = await async_client.chat.completions.create(
            model=model,
            messages=messages,
            response_format={"type": "json_object"},
            temperature=0.0,
        )
        response = json.loads(response.choices[0].message.content)
        await async_client.close()
        logger.info(response)
        return response
    except Exception as e:
        logger.error(f"Exception occured while creating metadata: {e}")
        raise (e)

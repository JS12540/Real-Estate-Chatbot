import os
import json
import asyncio
from openai import AsyncClient
from logger import logger
import sys

# Suppress encoding errors globally
sys.stdout.reconfigure(errors='ignore')

prompt = """
Given the following text, generate a response.
Do not generate any answer on your own. Describe the response based on the text as much as possible.
Response should be well phrased and in simple english.

Always give answer in markdown format.
""" 

async def generate_response(text):
    logger.info("Request received for generating response.")
    messages = [
        {"role": "system", "content": prompt},
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
            temperature=0.0,
        )
        response_text = (response.choices[0].message.content)
        await async_client.close()
        logger.info("Response Generated")
        return response_text
    except Exception as e:
        logger.error(f"Exception occured while generating response: {e}")
        raise (e)

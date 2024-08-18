import json
import os
from logger import logger
from openai import AsyncClient

MODULE_DESCRIPTION = """
information_retrieval

This module handles messages related to information retrieval, which can include:
- Requests for real estate data, any queries related to property brochure, property purchase
- Any queries related to property catalogue, property listing, or property sale
- Any queries related to tax inofrmation on properties
- Any queries realted to sales schemes and discounts
- Explanations and details related to property, catalogue, or property sale

inventory

This module handles messages related to inventory management, which can include:

- Queries related to the availability and status of units in a property, such as whether a specific unit is sold, available, or reserved.
- Requests for details on specific units, including unit type, size (sq ft.), floor, view, and price.
- Queries about parking availability, including the number of parking slots, slot size, and parking level associated with a unit.
- Inquiries related to the configuration and arrangement of units in a block or stack, such as floor plans, unit series, and stack organization.
- Requests for updates on inventory changes, such as new units added, price adjustments, or changes in availability status.
- Queries regarding the allocation or reassignment of parking slots in the inventory.
"""

CONTEXT = (
    "You are going to assist the chatbot by doing the following tasks:\n"
    "1. For each incoming query, classify it into one of the following modules, or None if no match is found:\n"  # noqa: E501
    f"{MODULE_DESCRIPTION}\n"
    "Do not guess any module on your own. Just extract it.\n"
    "Strictly classify each query into only one report or None. DO NOT GUESS\n"
    "Your Json response should look like this:\n"
    "{'classifications': [{'module': 'assigned report or None', 'reason': 'why this module was chosen or why no module was assigned'}]}\n"  # noqa: E501
    "Note: Each sub-query should be strictly classified into only one module or None."
)

EXAMPLES = """
Example 1 - INFORMATION RETRIEVAL Messages:
{"user_message": ['What are the taxes on properties and how it is calculated?', 'what are different sales schemes', 'Give me details about 3 bedroom + study unit']}
{
  'classifications': [
    {
      'module': 'information_retrieval',
      'reason': 'The user is inquiring about taxes on properties and how it is calculated.'
    },
    {
      'module': 'information_retrieval',
      'reason': 'The user is inquiring about different sales schemes.'
    },
    {
      'module': 'information_retrieval',
      'reason': 'The user is inquiring about details about 3 bedroom + study unit.'
    }
  ]
}

Example 2 - Inventory Messages:
{"user_message": ["What is the price and square footage of 1 Bed + Study?", 'Give me different properties which are not sold?']}
{
  'classifications': [
    {
      'module': 'inventory',
      'reason': 'The user is inquiring about the price and square footage of 1 Bed + Study.'
    },
    {
      'module': 'inventory',
      'reason': 'The user is inquiring about different properties which are not sold.'
    }
  ]
}

Example 3 - None Messages:

{"user_message": ['What is real estate', 'I want to invest in stocks']}
{
  'classifications': [
    {
      'module': 'None',
      'reason': 'The user is inquiring about real estate which is not related to information retrieval or inventory.'
    },
    {
      'module': 'None',
      'reason': 'The user is inquiring about investing in stocks which is not related to information retrieval or inventory.'
    }
  ]
}
"""


async def classify(query):
    """Asynchronously classifies a given query using the OpenAI API.

    Args:
        query (str): The query to be classified.
        phone_number (str): The phone number of the user.

    Returns:
        dict: The classification result in JSON format.

    Raises:
        None
    """
    logger.info(f"Classifying query: {query}")
    messages = [
        {"role": "system", "content": CONTEXT + EXAMPLES},
        {"role": "user", "content": str(query)},
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
        logger.info(f"Classification result: {response}")
        return response
    except Exception as e:
        logger.error(f"Exception occured while creating metadata: {e}")
        raise (e)
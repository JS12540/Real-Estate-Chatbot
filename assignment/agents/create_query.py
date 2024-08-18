import os
import json
import asyncio
from openai import AsyncClient
from logger import logger
import sys

# Suppress encoding errors globally
sys.stdout.reconfigure(errors='ignore')

create_query_prompt = """
Here are the columns in pandas:

Columns - Data Type - Unique Values (Example Values)
Floor - INT - Strcictly value between 1 to 21 inclusive.
Stack/series - INT - [1, 2, 3, 4, 5, 6, 7, 8]	
Unit number	- INT - Example value : 100
Unit type - STR - ["1 Bed + Study", "2 Bed", "2 Bed + Study", "3 Bed", "3 Bed + Study", "4 Bed"]
Area (sq ft.) - INT - Example value : 667	
View - STR - ['Pool', 'City']	
Price - INT - Example value in Dollars: 1273000	
Parking count - INT - [0,1,2]	
Parking Slot size - STR - ['2.5 * 4 meter', '2.5 * 5 meter']
Parking level - STR-  ['Basement', 'Level 1', 'Level 2', 'Level 3', 'Level 4', 'Level 5']	
Sold? - STR -  ['Yes', 'No']

The dataframe is df and exmaple query is  "SELECT * FROM df WHERE `Sold?` = 'No'"

Given a user query create a SQL query that can be used in pandas to query the csv and get details about the properties.
""" 

async def create_query(text):
    messages = [
        {"role": "system", "content": create_query_prompt},
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
        response_text = response.choices[0].message.content
        # Clean up the response by removing code block backticks and the "sql" keyword
        cleaned_response = response_text.replace("```sql", "").replace("```", "").strip()
        await async_client.close()
        logger.info(f"Created query: {cleaned_response}")
        return cleaned_response
    except Exception as e:
        logger.error(f"Exception occured while creating metadata: {e}")
        raise (e)

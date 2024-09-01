from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from agents.classifier import classify
from agents.create_query import create_query
from execute_query import execute_query_on_csv
from agents.generate_response import generate_response
from vector_store.atlas_vector import AtlasVectorStore
from utils import get_cached_response, store_cache, get_fuzzy_cached_response
from logger import logger

avs = AtlasVectorStore()
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Adjust as needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/ping")
def ping():
    return {"ping": "pong"}    

@app.post("/query")
async def submit_query(query):
    try:
        logger.info(f"Processing query: {query}")

        # Check exact cache match in MongoDB
        cached_response = await get_cached_response(query)
        if cached_response:
            logger.info("Exact cache hit for query.")
            return {"bot_response": cached_response}
        
        # If no exact match, check fuzzy match in MongoDB
        cached_response = await get_fuzzy_cached_response(query)
        if cached_response:
            return {"bot_response": cached_response}
        
        response = await classify(query)
        classification = response["classifications"][0]["module"]
        
        if classification == "information_retrieval":
            results = avs.retrieve(query=query)
            logger.info(f"Length of results: {len(results)}")
            merged_text = " ".join(doc.page_content for doc in results)
            logger.info("Sending text to generate bot response")
            bot_response = await generate_response(merged_text)
            await store_cache(query=query, response=bot_response)
            return {"bot_response": bot_response}
        elif classification == "inventory":
            sql_query = await create_query(query)
            markdown_text = execute_query_on_csv(sql_query)
            await store_cache(query=query, response=markdown_text)
            return {"bot_response": markdown_text}
        else:
            bot_response = "Sorry, I don't have information for that query. Would you like to call a human?"
            await store_cache(query=query, response=bot_response)
            return {"bot_response": bot_response}
    except Exception as e:
        logger.error(f"Exception occured while processing query: {e}")
        return {"message": "Error processing query", "details": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

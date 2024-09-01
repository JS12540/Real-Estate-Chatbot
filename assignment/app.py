from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from agents.classifier import classify
from agents.create_query import create_query
from execute_query import execute_query_on_csv
from agents.generate_response import generate_response
from vector_store.atlas_vector import AtlasVectorStore
from logger import logger
from cache.mongodb_cache import MongoDBSemanticCache


avs = AtlasVectorStore()
app = FastAPI()
semantic_cache=MongoDBSemanticCache(
            score_threshold=0.97
        )


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
        
        # If no exact match, check semantic match in MongoDB
        semantic_response = semantic_cache.lookup(query, llm_string="gpt-4o-mini")
        if semantic_response:
            logger.info("Semantic cache hit for query.")
            return {"bot_response": semantic_response}
        
        response = await classify(query)
        classification = response["classifications"][0]["module"]
        
        if classification == "information_retrieval":
            results = avs.retrieve(query=query)
            logger.info(f"Length of results: {len(results)}")
            merged_text = " ".join(doc.page_content for doc in results)
            logger.info("Sending text to generate bot response")
            bot_response = await generate_response(merged_text)
            semantic_cache.update(query, llm_string="gpt-4o-mini", response=bot_response)
            return {"bot_response": bot_response}
        elif classification == "inventory":
            sql_query = await create_query(query)
            markdown_text = execute_query_on_csv(sql_query)
            semantic_cache.update(query, llm_string="gpt-4o-mini", response=markdown_text)
            return {"bot_response": markdown_text}
        else:
            bot_response = "Sorry, I don't have information for that query. Would you like to call a human?"
            semantic_cache.update(query, llm_string="gpt-4o-mini", response=bot_response)
            return {"bot_response": bot_response}
    except Exception as e:
        logger.error(f"Exception occured while processing query: {e}")
        return {"message": "Error processing query", "details": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

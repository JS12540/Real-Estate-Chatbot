from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from agents.classifier import classify
from agents.create_query import create_query
from execute_query import execute_query_on_csv
from agents.generate_response import generate_response
from vector_store.atlas_vector import AtlasVectorStore
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
        response = await classify(query)
        classification = response["classifications"][0]["module"]
        
        if classification == "information_retrieval":
            results = avs.retrieve(query=query)
            logger.info(f"Length of results: {len(results)}")
            # Extract and merge text from results
            merged_text = " ".join(doc.page_content for doc in results)
            logger.info("Sending text to generate bot response")
            # Generate a response using the merged text
            bot_response = await generate_response(merged_text)
            return {"bot_response": bot_response}
        elif classification == "inventory":
            sql_query = await create_query(query)
            markdown_text = execute_query_on_csv(sql_query)
            return {"bot_response": markdown_text}
        else:
            return {"bot_response": "Sorry, I don't have information for that query. Would you like to call a human?"}
    except Exception as e:
        logger.error(f"Exception occured while processing query: {e}")
        return {"message": "Error processing query", "details": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

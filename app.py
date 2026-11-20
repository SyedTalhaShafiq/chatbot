import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import config
import pipeline
import dynamo_service
import cloud_utils

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TML-Bot-API")

ml_models = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    1. Downloads Vector DB from S3.
    2. Loads RAG Pipeline.
    """
    logger.info("[-] Server Startup: Initializing...")
    config.setup_logging()
    
    cloud_utils.download_index_from_s3()
    
    try:
        engine, guard = pipeline.build_rag_pipeline()
        ml_models["engine"] = engine
        ml_models["guard"] = guard
        logger.info("[-] Pipeline Ready! API is listening.")
    except Exception as e:
        logger.error(f"[!] Critical Startup Failure: {e}")
        pass 
        
    yield
    
    ml_models.clear()
    logger.info("[-] Server Shutdown.")

app = FastAPI(title="TML Logistics Bot API", lifespan=lifespan)

class ChatRequest(BaseModel):
    email: str
    query: str

class ChatResponse(BaseModel):
    response: str
    status: str = "success"

@app.post("/chat", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest):
    engine = ml_models.get("engine")
    guard = ml_models.get("guard")

    if not engine or not guard:
        raise HTTPException(status_code=503, detail="AI Models not initialized.")

    logger.info(f"[{request.email}] Incoming Query: {request.query}")

    final_response = ""
    status_code = "success"

    is_safe, reason = guard.check(request.query)
    
    if not is_safe:
        logger.warning(f"[{request.email}] Blocked: {reason}")
        final_response = f"{reason}"
        status_code = "blocked"
    else:
        try:
            result = engine.query(request.query)
            final_response = str(result)
            logger.info(f"[{request.email}] Success.")
        except Exception as e:
            logger.error(f"[{request.email}] RAG Error: {e}")
            final_response = "I encountered an internal error."
            status_code = "error"

    dynamo_service.save_chat_log(
        email=request.email,
        query=request.query,
        response=final_response,
        status=status_code
    )

    return ChatResponse(response=final_response, status=status_code)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
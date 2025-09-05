from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from ..core.config import settings
from ..core.models import ChatRequest, ChatResponse, ChatHistoryResponse
from ..core.services import process_query, get_history

app = FastAPI(
    title=settings.app_title,
    version=settings.app_version,
    description="API for chat interactions"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": settings.app_title,
        "endpoints": {
            "POST /chat": "Send a query to Cohere Chat API with Wikipedia tool integration",
            "GET /chat/history": "Retrieve complete chat history",
        },
        "version": settings.app_version
    }

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    try:
        result = await process_query(request.query)
        return ChatResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/chat/history", response_model=ChatHistoryResponse)
async def get_chat_history():
    try:
        result = await get_history()
        return ChatHistoryResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "src.api.routes:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
# main.py - COMPLETE WITH CHAT ENDPOINT
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict
from upload import router
from rag_engine import RAGTutor
from dotenv import load_dotenv
import logging

load_dotenv()


logging.basicConfig(level=logging.INFO)

app = FastAPI(title="PrepMate API")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


tutor = None

# @app.on_event("startup")
# async def startup_event():
#     global tutor
#     print("🚀 Starting PrepMate API...")
#     try:
#         tutor = RAGTutor()
#         print("✅ PrepMate ready!")
#     except Exception as e:
#         print(f"❌ Failed to initialize RAG: {e}")
#         raise

@app.on_event("startup")
async def startup_event():
    print("🚀 Starting...")
    tutor = None  # Skip RAG
    print("✅ Ready!")


app.include_router(router)


@app.get("/")
def welcome():
    return {
        "status": "healthy",
        "message": "Backend successfully connected",
        "service": "PrepMate API",
        "endpoints": {
            "upload": "/upload/multiple",
            "chat": "/chat/",
            "docs": "/docs"
        }
    }

class ChatRequest(BaseModel):
    message: str
    chat_history: List[Dict] = []

@app.post("/chat/")
async def chat_endpoint(request: ChatRequest):
    """
    Chat with RAG tutor
    """
    logging.info(f"Chat request: {request.message[:50]}...")
    
    try:
        if tutor is None:
            logging.error("RAG Tutor not initialized")
            return {
                "success": False,
                "error": "RAG Tutor not initialized. Please restart the server."
            }
        
    
        result = tutor.chat(request.message, request.chat_history)
        
        logging.info(f"Chat response generated. Sources: {result.get('sources_used', 0)}")
        
        return {
            "success": True,
            "data": result
        }
    
    except Exception as e:
        logging.error(f"Error in chat endpoint: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e)
        }
class FlashcardRequest(BaseModel):
    """Request model for flashcard generation"""
    topic: str
    num_cards: int = 10

@app.post("/flashcards")
async def flashcards_endpoint(request: FlashcardRequest):
    """
    Generate flashcards on a topic
    
    Args:
        request: FlashcardRequest with topic and number of cards
        
    Returns:
        JSON with generated flashcards
    """
    logging.info(f"🗂️ Flashcard request: {request.topic} ({request.num_cards} cards)")
    
    try:
        if tutor is None:
            logging.error("RAG Tutor not initialized")
            return {
                "success": False,
                "error": "RAG Tutor not initialized. Please restart the server."
            }
        
        # Call RAG engine flashcard generation
        result = tutor.generate_flashcards(request.topic, request.num_cards)
        
        logging.info(f"✅ Flashcards generated: {request.num_cards} cards")
        
        return {
            "success": True,
            "data": result
        }
    
    except Exception as e:
        logging.error(f"❌ Error in flashcards endpoint: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e)
        }

@app.post("/clear")
async def clear_documents():
    """
    Clear all documents from Pinecone
    """
    try:
        from converter import clear_pinecone_index
        
        success = clear_pinecone_index()
        
        if success:
            return {
                "success": True,
                "message": "All documents cleared from knowledge base"
            }
        else:
            return {
                "success": False,
                "error": "Failed to clear documents"
            }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


# Health check
@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "rag_initialized": tutor is not None
    }

# Run
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
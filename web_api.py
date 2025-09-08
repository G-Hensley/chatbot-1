"""
FastAPI Web Interface for The Intersect Portfolio Chatbot
Secure API endpoints for website integration with rate limiting and CORS support.
"""

from fastapi import FastAPI, HTTPException, Depends, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, List
import time
import hashlib
import os
from collections import defaultdict, deque
import asyncio
from contextlib import asynccontextmanager
import logging

from ollama_chatbot import OllamaPortfolioChatbot

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Security configurations
API_KEY = os.getenv("INTERSECT_API_KEY", "your-super-secret-api-key-change-this")
RATE_LIMIT_REQUESTS = 10  # requests per minute per IP
RATE_LIMIT_WINDOW = 60   # seconds

# Rate limiting storage
rate_limit_storage = defaultdict(lambda: deque())

# Initialize chatbot globally
chatbot = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global chatbot
    logger.info("🚀 Starting The Intersect API...")
    
    try:
        chatbot = OllamaPortfolioChatbot()
        connected, message = chatbot.check_ollama_connection()
        
        if not connected:
            logger.error(f"❌ Ollama connection failed: {message}")
            raise Exception(f"Ollama not available: {message}")
        
        logger.info(f"✅ Connected to Ollama with model: {chatbot.model_name}")
        logger.info(f"📊 Loaded {len(chatbot.dataset_manager.data['conversations'])} knowledge entries")
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize chatbot: {str(e)}")
        raise
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down The Intersect API...")

# Create FastAPI app
app = FastAPI(
    title="The Intersect - Portfolio Chatbot API",
    description="Secure API for Brenda Hensley's AI knowledge database",
    version="1.0.0",
    docs_url="/docs",  # Swagger UI
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS middleware for website integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React dev server
        "http://localhost:8080",  # Vue dev server
        "https://tampertantrumlabs.com",  # Your production domain
        "https://www.tampertantrumlabs.com",  # www version
        # Add your actual domain here
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Security scheme
security = HTTPBearer(auto_error=False)

# Pydantic models
class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=500, description="User message to the chatbot")
    conversation_id: Optional[str] = Field(None, description="Optional conversation ID for context")

class ChatResponse(BaseModel):
    response: str = Field(..., description="Chatbot response")
    conversation_id: str = Field(..., description="Conversation ID for maintaining context")
    timestamp: float = Field(..., description="Response timestamp")
    processing_time: float = Field(..., description="Response processing time in seconds")

class HealthResponse(BaseModel):
    status: str
    model: str
    dataset_size: int
    uptime: float

class ErrorResponse(BaseModel):
    error: str
    details: Optional[str] = None

# Rate limiting function
def check_rate_limit(client_ip: str) -> bool:
    """Check if client has exceeded rate limit."""
    now = time.time()
    client_requests = rate_limit_storage[client_ip]
    
    # Remove old requests outside the window
    while client_requests and client_requests[0] <= now - RATE_LIMIT_WINDOW:
        client_requests.popleft()
    
    # Check if under limit
    if len(client_requests) >= RATE_LIMIT_REQUESTS:
        return False
    
    # Add current request
    client_requests.append(now)
    return True

# Authentication function
def verify_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)) -> bool:
    """Verify API key from Authorization header."""
    if not credentials:
        return False
    
    # Simple API key validation (in production, use more sophisticated auth)
    return credentials.credentials == API_KEY

# Dependency for rate limiting
def rate_limit_dependency(request: Request):
    """Rate limiting dependency."""
    client_ip = request.client.host
    
    if not check_rate_limit(client_ip):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded. Maximum {RATE_LIMIT_REQUESTS} requests per minute."
        )

# Dependency for authentication (optional - uncomment to enable)
def auth_dependency(authenticated: bool = Depends(verify_api_key)):
    """Authentication dependency."""
    if not authenticated:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
            headers={"WWW-Authenticate": "Bearer"},
        )

# In-memory conversation storage (use Redis in production)
conversations = {}

@app.get("/", response_model=dict)
async def root():
    """Root endpoint with API information."""
    return {
        "name": "The Intersect - Portfolio Chatbot API",
        "description": "Secure API for Brenda Hensley's AI knowledge database",
        "version": "1.0.0",
        "endpoints": {
            "chat": "/api/v1/chat",
            "health": "/api/v1/health",
            "docs": "/docs"
        }
    }

@app.get("/api/v1/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    global chatbot
    
    if not chatbot:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Chatbot not initialized"
        )
    
    connected, message = chatbot.check_ollama_connection()
    
    if not connected:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Ollama not available: {message}"
        )
    
    return HealthResponse(
        status="healthy",
        model=chatbot.model_name,
        dataset_size=len(chatbot.dataset_manager.data['conversations']),
        uptime=time.time()
    )

@app.post("/api/v1/chat", response_model=ChatResponse)
async def chat_endpoint(
    request: ChatRequest,
    client_request: Request,
    _: None = Depends(rate_limit_dependency),
    # _auth: None = Depends(auth_dependency)  # Uncomment to enable auth
):
    """
    Main chat endpoint for The Intersect.
    
    - **message**: Your question or message to The Intersect
    - **conversation_id**: Optional ID to maintain conversation context
    """
    global chatbot
    
    if not chatbot:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Chatbot service unavailable"
        )
    
    start_time = time.time()
    
    try:
        # Generate conversation ID if not provided
        conversation_id = request.conversation_id
        if not conversation_id:
            conversation_id = hashlib.md5(
                f"{client_request.client.host}_{time.time()}".encode()
            ).hexdigest()[:16]
        
        # Get conversation history
        conversation_history = conversations.get(conversation_id, [])
        
        # Get response from chatbot
        response = chatbot.chat_with_ollama(request.message, conversation_history)
        
        # Update conversation history
        conversation_history.append({"role": "user", "content": request.message})
        conversation_history.append({"role": "assistant", "content": response})
        
        # Keep conversation history manageable (last 10 exchanges)
        if len(conversation_history) > 20:
            conversation_history = conversation_history[-20:]
        
        conversations[conversation_id] = conversation_history
        
        processing_time = time.time() - start_time
        
        # Log the interaction
        logger.info(f"Chat response generated in {processing_time:.2f}s for IP: {client_request.client.host}")
        
        return ChatResponse(
            response=response,
            conversation_id=conversation_id,
            timestamp=time.time(),
            processing_time=processing_time
        )
        
    except Exception as e:
        logger.error(f"Error processing chat request: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing request: {str(e)}"
        )

@app.delete("/api/v1/chat/{conversation_id}")
async def clear_conversation(
    conversation_id: str,
    _: None = Depends(rate_limit_dependency)
):
    """Clear conversation history for a specific conversation ID."""
    if conversation_id in conversations:
        del conversations[conversation_id]
        return {"message": f"Conversation {conversation_id} cleared"}
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )

@app.get("/api/v1/stats")
async def get_stats(
    _: None = Depends(rate_limit_dependency)
):
    """Get API usage statistics."""
    return {
        "active_conversations": len(conversations),
        "total_rate_limit_entries": len(rate_limit_storage),
        "dataset_categories": len(chatbot.dataset_manager.get_all_categories()) if chatbot else 0
    }

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Custom HTTP exception handler."""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(error=exc.detail).dict()
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """General exception handler."""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            error="Internal server error",
            details="An unexpected error occurred"
        ).dict()
    )

if __name__ == "__main__":
    import uvicorn
    
    print("🤖 Starting The Intersect API Server...")
    print("📚 API Documentation available at: http://localhost:8000/docs")
    print("🔗 Health check: http://localhost:8000/api/v1/health")
    print("💬 Chat endpoint: POST http://localhost:8000/api/v1/chat")
    
    uvicorn.run(
        "web_api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

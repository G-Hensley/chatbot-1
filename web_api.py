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
import requests
from collections import defaultdict, deque
import asyncio
from contextlib import asynccontextmanager
import logging

from groq_chatbot import GroqPortfolioChatbot

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Security configurations
API_KEY = os.getenv("INTERSECT_API_KEY", "your-super-secret-api-key-change-this")
RATE_LIMIT_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", "10"))  # requests per minute per IP
RATE_LIMIT_WINDOW = int(os.getenv("RATE_LIMIT_WINDOW", "60"))     # seconds

# Railway environment detection
IS_RAILWAY = os.getenv("RAILWAY_ENVIRONMENT") == "production"
PORT = int(os.getenv("PORT", "8080"))

# Rate limiting storage
rate_limit_storage = defaultdict(lambda: deque())

def get_fallback_response(message: str) -> str:
    """Provide helpful fallback responses when Groq is unavailable."""
    message_lower = message.lower()
    
    # Determine response based on message content
    if any(word in message_lower for word in ["brenda", "about", "experience", "background"]):
        return """I'm The Intersect, Brenda Hensley's AI knowledge database. While my full AI capabilities are temporarily unavailable, I can tell you that Brenda is an AppSec Engineer specializing in cybersecurity. 

For detailed information about her experience, services, and background, please visit:
🌐 Website: https://tampertantrumlabs.com
📧 Email: hensley.brenda@protonmail.com

I'll be back to full functionality shortly!"""
    
    elif any(word in message_lower for word in ["services", "offer", "business", "tampertantrum"]):
        return """TamperTantrum Labs offers comprehensive cybersecurity services including:
• Application Security Engineering
• Security Assessments & Penetration Testing
• Cybersecurity Consulting

While my AI processing is temporarily offline, you can get full details at:
🌐 https://tampertantrumlabs.com
📧 hensley.brenda@protonmail.com"""
    
    elif any(word in message_lower for word in ["contact", "email", "reach", "connect"]):
        return """You can reach Brenda Hensley at:
📧 hensley.brenda@protonmail.com
🌐 https://tampertantrumlabs.com

I'm The Intersect - Brenda's AI assistant. I'm experiencing technical difficulties right now, but I'll be back soon with full conversational capabilities!"""
    
    else:
        return """Hello! I'm The Intersect, Brenda Hensley's AI knowledge database. I'm currently experiencing technical difficulties with my AI processing, but I can still help you with basic information.

Brenda is a cybersecurity expert specializing in AppSec Engineering. For detailed information, please visit:
🌐 https://tampertantrumlabs.com
📧 hensley.brenda@protonmail.com

I should be back to full functionality shortly. Thank you for your patience!"""

# Initialize chatbot globally
chatbot = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global chatbot
    logger.info("🚀 Starting The Intersect API...")
    
    try:
        chatbot = GroqPortfolioChatbot()
        connected, message = chatbot.check_connection()
        
        if not connected:
            logger.warning(f"⚠️ Groq connection failed: {message}")
            logger.info("🔄 API will start without Groq. Configure GROQ_API_KEY environment variable.")
            # Don't raise exception - let API start and show helpful error messages
        else:
            logger.info(f"✅ Connected to Ollama with model: {chatbot.model_name}")
            logger.info(f"📊 Loaded {len(chatbot.dataset_manager.data['conversations'])} knowledge entries")
        
    except Exception as e:
        logger.warning(f"⚠️ Failed to initialize chatbot: {str(e)}")
        logger.info("🔄 API starting in degraded mode. Check Ollama configuration.")
        chatbot = None  # Set to None so we can handle it gracefully
    
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
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "").split(",") if os.getenv("ALLOWED_ORIGINS") else [
    "http://localhost:3000",  # React dev server
    "http://localhost:8080",  # Vue dev server
    "https://tampertantrumlabs.com",  # Your production domain
    "https://www.tampertantrumlabs.com",  # www version
    # Add your actual domain here
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
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
    global chatbot
    
    if not chatbot:
        return {
            "name": "The Intersect - Portfolio Chatbot API",
            "description": "Brenda Hensley's AI knowledge database",
            "version": "1.0.0",
            "status": "⚠️ OLLAMA NOT CONFIGURED",
            "setup_required": "Please set OLLAMA_URL environment variable and ensure Ollama is running",
            "endpoints": {
                "health": "/api/v1/health",
                "setup": "/api/v1/setup",
                "docs": "/docs"
            },
            "instructions": "Visit /api/v1/setup for configuration help"
        }
    
    connected, message = chatbot.check_connection()
    
    return {
        "name": "The Intersect - Portfolio Chatbot API",
        "description": "Secure API for Brenda Hensley's AI knowledge database",
        "version": "1.0.0",
        "status": "✅ READY" if connected else f"⚠️ OLLAMA ISSUE: {message}",
        "endpoints": {
            "chat": "/api/v1/chat",
            "health": "/api/v1/health",
            "stats": "/api/v1/stats",
            "docs": "/docs"
        }
    }

@app.get("/api/v1/setup")
async def setup_instructions():
    """Provide setup instructions for configuring Ollama."""
    global chatbot
    
    ollama_url = os.getenv("OLLAMA_URL", "not_set")
    ollama_model = os.getenv("OLLAMA_MODEL", "llama3.1")
    
    setup_info = {
        "title": "🚀 The Intersect API Setup Instructions",
        "current_config": {
            "OLLAMA_URL": ollama_url,
            "OLLAMA_MODEL": ollama_model,
            "chatbot_initialized": chatbot is not None
        },
        "steps": [
            {
                "step": 1,
                "title": "Set Environment Variables in Railway",
                "variables": {
                    "OLLAMA_URL": "https://your-ollama-instance.railway.app (or external URL)",
                    "OLLAMA_MODEL": "llama3.1",
                    "INTERSECT_API_KEY": "your-secure-api-key",
                    "ALLOWED_ORIGINS": "https://tampertantrumlabs.com"
                }
            },
            {
                "step": 2, 
                "title": "Deploy Ollama Service",
                "options": [
                    "Option A: Create new Railway service with ollama/ollama:latest image",
                    "Option B: Use external Ollama server (DigitalOcean, AWS, etc.)",
                    "Option C: Use local Ollama for development"
                ]
            },
            {
                "step": 3,
                "title": "Pull Model in Ollama",
                "command": f"ollama pull {ollama_model}"
            },
            {
                "step": 4,
                "title": "Restart Railway Service",
                "note": "After setting environment variables, redeploy this service"
            }
        ],
        "test_endpoints": {
            "health": "/api/v1/health",
            "documentation": "/docs"
        }
    }
    
    if chatbot:
        connected, message = chatbot.check_connection()
        setup_info["connection_test"] = {
            "connected": connected,
            "message": message,
            "status": "✅ Ready!" if connected else f"❌ {message}"
        }
    
    return setup_info

@app.get("/api/v1/setup")
async def setup_instructions():
    """Provide setup instructions for configuring Ollama."""
    global chatbot
    
    ollama_url = os.getenv("OLLAMA_URL", "not_set")
    ollama_model = os.getenv("OLLAMA_MODEL", "llama3.1")
    
    setup_info = {
        "title": "🚀 The Intersect API Setup Instructions",
        "current_config": {
            "OLLAMA_URL": ollama_url,
            "OLLAMA_MODEL": ollama_model,
            "chatbot_initialized": chatbot is not None
        },
        "steps": [
            {
                "step": 1,
                "title": "Set Environment Variables in Railway",
                "variables": {
                    "OLLAMA_URL": "https://your-ollama-instance.railway.app (or external URL)",
                    "OLLAMA_MODEL": "llama3.1",
                    "INTERSECT_API_KEY": "your-secure-api-key",
                    "ALLOWED_ORIGINS": "https://tampertantrumlabs.com"
                }
            },
            {
                "step": 2, 
                "title": "Deploy Ollama Service",
                "options": [
                    "Option A: Create new Railway service with ollama/ollama:latest image",
                    "Option B: Use external Ollama server (DigitalOcean, AWS, etc.)",
                    "Option C: Use local Ollama for development"
                ]
            },
            {
                "step": 3,
                "title": "Pull Model in Ollama",
                "command": f"ollama pull {ollama_model}"
            },
            {
                "step": 4,
                "title": "Restart Railway Service",
                "note": "After setting environment variables, redeploy this service"
            }
        ],
        "test_endpoints": {
            "health": "/api/v1/health",
            "documentation": "/docs"
        }
    }
    
    if chatbot:
        connected, message = chatbot.check_connection()
        setup_info["connection_test"] = {
            "connected": connected,
            "message": message,
            "status": "✅ Ready!" if connected else f"❌ {message}"
        }
    
    return setup_info

@app.get("/api/v1/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    global chatbot
    
    if not chatbot:
        # Return helpful information even when Ollama isn't connected
        return HealthResponse(
            status="degraded",
            model="not_connected", 
            dataset_size=0,
            uptime=time.time()
        )
    
    connected, message = chatbot.check_connection()
    
    if not connected:
        return HealthResponse(
            status="degraded",
            model=f"error: {message}",
            dataset_size=len(chatbot.dataset_manager.data['conversations']) if chatbot.dataset_manager else 0,
            uptime=time.time()
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
            detail="Chatbot service unavailable. Please configure OLLAMA_URL environment variable and ensure Ollama is running."
        )
    
    # Check Ollama connection before processing
    connected, message = chatbot.check_connection()
    if not connected:
        # Provide fallback response when Ollama is unavailable
        fallback_response = get_fallback_response(request.message)
        
        processing_time = time.time() - start_time
        
        return ChatResponse(
            response=fallback_response,
            conversation_id=request.conversation_id or "fallback",
            timestamp=time.time(),
            processing_time=processing_time
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
        response = chatbot.chat_with_groq(request.message, conversation_history)
        
        # Check for special error flags and provide fallback
        if response.startswith("GROQ_ERROR:"):
            logger.warning(f"Groq error for IP: {client_request.client.host} - {response}")
            fallback_response = get_fallback_response(request.message)
            processing_time = time.time() - start_time
            
            return ChatResponse(
                response=fallback_response + "\n\n⚠️ Note: AI system is temporarily unavailable. Providing basic information instead.",
                conversation_id=request.conversation_id or "ai_fallback",
                timestamp=time.time(),
                processing_time=processing_time
            )
        
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
        
    except requests.exceptions.Timeout:
        logger.warning(f"Ollama request timed out for IP: {client_request.client.host}")
        # Return fallback response on timeout
        fallback_response = get_fallback_response(request.message)
        processing_time = time.time() - start_time
        
        return ChatResponse(
            response=fallback_response + "\n\n⚠️ Note: AI response timed out, providing basic information instead.",
            conversation_id=request.conversation_id or "timeout_fallback",
            timestamp=time.time(),
            processing_time=processing_time
        )
    except Exception as e:
        logger.error(f"Error processing chat request: {str(e)}")
        # Also provide fallback for other errors
        fallback_response = get_fallback_response(request.message)
        processing_time = time.time() - start_time
        
        return ChatResponse(
            response=fallback_response + f"\n\n⚠️ Technical issue encountered: {str(e)[:100]}...",
            conversation_id=request.conversation_id or "error_fallback",
            timestamp=time.time(),
            processing_time=processing_time
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
    
    # Use Railway's port or default to 8000
    port = int(os.getenv("PORT", "8080"))
    host = "0.0.0.0"
    
    print("🤖 Starting The Intersect API Server...")
    print(f"📚 API Documentation available at: http://localhost:{port}/docs")
    print(f"🔗 Health check: http://localhost:{port}/api/v1/health")
    print(f"💬 Chat endpoint: POST http://localhost:{port}/api/v1/chat")
    
    if IS_RAILWAY:
        print("🚂 Running on Railway!")
        print(f"🌐 CORS origins: {ALLOWED_ORIGINS}")
    
    uvicorn.run(
        "web_api:app",
        host=host,
        port=port,
        reload=not IS_RAILWAY,  # Disable reload in production
        log_level="info"
    )

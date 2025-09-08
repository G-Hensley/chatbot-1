# 🚀 The Intersect - Web API Deployment Guide

## 🎯 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Start Ollama (if not running)
```bash
python setup_ollama.py
```

### 3. Start the FastAPI Server
```bash
python web_api.py
```

Your API will be available at:
- **API**: http://localhost:8000
- **Docs**: http://localhost:8000/docs
- **Health**: http://localhost:8000/api/v1/health
- **Demo**: Open `chat_demo.html` in your browser

## 🔒 Security Configuration

### API Key Authentication (Optional)
1. Copy `.env.example` to `.env`
2. Set your API key:
```bash
INTERSECT_API_KEY=your-super-secret-api-key-here
```
3. Uncomment the auth dependency in `web_api.py`:
```python
_auth: None = Depends(auth_dependency)  # Uncomment this line
```

### CORS Configuration
Update allowed origins in `web_api.py`:
```python
allow_origins=[
    "https://yourdomain.com",
    "https://www.yourdomain.com",
]
```

## 📡 API Endpoints

### POST `/api/v1/chat`
Send a message to The Intersect.

**Request:**
```json
{
  "message": "Tell me about Brenda's skills",
  "conversation_id": "optional-conversation-id"
}
```

**Response:**
```json
{
  "response": "Brenda's core skills include...",
  "conversation_id": "abc123",
  "timestamp": 1694123456.789,
  "processing_time": 2.34
}
```

### GET `/api/v1/health`
Check API health status.

**Response:**
```json
{
  "status": "healthy",
  "model": "llama3.1",
  "dataset_size": 31,
  "uptime": 12345.67
}
```

### DELETE `/api/v1/chat/{conversation_id}`
Clear conversation history.

### GET `/api/v1/stats`
Get usage statistics.

## 🌐 Website Integration

### Option 1: Simple JavaScript SDK
```html
<script src="intersect-sdk.js"></script>
<script>
const intersect = new IntersectSDK('http://localhost:8000');

async function askQuestion() {
    try {
        const response = await intersect.chat('Tell me about Brenda');
        console.log(response.response);
    } catch (error) {
        console.error('Error:', error.message);
    }
}
</script>
```

### Option 2: Chat Widget
```html
<div id="chat-widget"></div>
<script src="intersect-sdk.js"></script>
<script>
new IntersectChatWidget('http://localhost:8000', 'chat-widget');
</script>
```

### Option 3: Custom Fetch
```javascript
async function chatWithIntersect(message) {
    const response = await fetch('http://localhost:8000/api/v1/chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            // 'Authorization': 'Bearer your-api-key'  // If using auth
        },
        body: JSON.stringify({ message })
    });
    
    return await response.json();
}
```

## 🐳 Docker Deployment

### Using Docker Compose (Recommended)
```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Manual Docker Build
```bash
# Build image
docker build -t intersect-api .

# Run container
docker run -p 8000:8000 \
  -e INTERSECT_API_KEY=your-api-key \
  -e OLLAMA_URL=http://host.docker.internal:11434 \
  intersect-api
```

## ☁️ Cloud Deployment

### Deploy to Railway
1. Connect your GitHub repo to Railway
2. Set environment variables:
   - `INTERSECT_API_KEY`: Your API key
   - `OLLAMA_URL`: Your Ollama instance URL
3. Deploy!

### Deploy to Heroku
```bash
# Install Heroku CLI
heroku create your-intersect-api

# Set environment variables
heroku config:set INTERSECT_API_KEY=your-api-key
heroku config:set OLLAMA_URL=your-ollama-url

# Deploy
git push heroku main
```

### Deploy to DigitalOcean App Platform
1. Create new app from GitHub
2. Set environment variables
3. Configure auto-deploy

## 🔧 Rate Limiting

Default settings:
- **10 requests per minute** per IP address
- **60-second** rate limit window

Configure in `.env`:
```bash
RATE_LIMIT_REQUESTS=20
RATE_LIMIT_WINDOW=60
```

## 📊 Monitoring

### Health Checks
```bash
curl http://localhost:8000/api/v1/health
```

### View Logs
```bash
# With Docker Compose
docker-compose logs -f intersect-api

# Direct Python
python web_api.py  # Logs to console
```

### API Statistics
```bash
curl http://localhost:8000/api/v1/stats
```

## 🛠️ Troubleshooting

### Ollama Connection Issues
1. Make sure Ollama is running: `ollama serve`
2. Check model is pulled: `ollama list`
3. Test connection: `curl http://localhost:11434/api/tags`

### CORS Errors
Add your domain to `allow_origins` in `web_api.py`

### Rate Limit Issues
Increase limits in configuration or implement IP whitelisting

### Performance Issues
- Use smaller model (llama2 instead of llama3.1)
- Increase server resources
- Implement response caching

## 🚀 Production Checklist

- [ ] Set strong API key
- [ ] Configure CORS for your domain
- [ ] Set up proper logging
- [ ] Configure rate limiting
- [ ] Set up monitoring/health checks
- [ ] Use HTTPS in production
- [ ] Configure proper firewall rules
- [ ] Set up automated backups
- [ ] Test error handling
- [ ] Load test the API

## 💡 Advanced Features

### Add Authentication Middleware
```python
from fastapi import Security
from fastapi.security import HTTPBearer

security = HTTPBearer()

@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    # Custom auth logic here
    response = await call_next(request)
    return response
```

### Add Response Caching
```python
from functools import lru_cache

@lru_cache(maxsize=100)
def cached_response(message_hash):
    # Cache frequently asked questions
    pass
```

### Add Conversation Analytics
```python
# Track conversation metrics
conversation_metrics = {
    'total_messages': 0,
    'avg_response_time': 0,
    'popular_topics': []
}
```

## 📞 Support

For issues or questions:
- Check the logs first
- Review the FastAPI docs at `/docs`
- Test with the demo HTML file
- Check Ollama status and logs

Your chatbot API is now ready for production! 🎉

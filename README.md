# The Intersect - Brenda's Portfolio Chatbot API

A production-ready FastAPI chatbot service powered by Ollama, designed to answer questions about Brenda Hensley's cybersecurity expertise and services.

## 🚀 Live Deployment

This chatbot is deployed on Railway and ready for website integration.

**API Endpoints:**
- Health Check: `GET /api/v1/health`
- Chat: `POST /api/v1/chat`
- Documentation: `GET /docs`

## 📁 Project Structure

```
├── web_api.py              # Main FastAPI application
├── ollama_chatbot.py       # Core chatbot logic with Ollama integration
├── dataset_manager.py      # Portfolio data management
├── portfolio_dataset.json  # Brenda's knowledge base (30 conversations)
├── requirements.txt        # Python dependencies
├── railway.toml           # Railway deployment configuration
├── nixpacks.toml          # Build optimization for Railway
├── .railwayignore         # Files excluded from deployment
└── README.md              # This file
```

## 🤖 The Intersect Features

- **AI Persona**: "The Intersect" - Brenda's AI knowledge database
- **Portfolio Information**: Background, skills, certifications, services
- **CTF Easter Eggs**: Hidden challenges and personality traits
- **Security Focus**: Application security expertise and TamperTantrum Labs
- **Professional Tone**: Tech-savvy but approachable responses

## 🔌 API Usage

### Chat Endpoint
```bash
POST /api/v1/chat
Content-Type: application/json

{
  "message": "Tell me about Brenda's cybersecurity experience",
  "conversation_id": "optional-for-context"
}
```

### Response
```json
{
  "response": "Brenda has 1 year of professional AppSec experience...",
  "conversation_id": "abc123",
  "timestamp": 1694123456.789,
  "processing_time": 2.34
}
```

## 🌐 Website Integration

```javascript
// Simple fetch example
const response = await fetch('https://your-api-url.railway.app/api/v1/chat', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({message: 'What are your main skills?'})
});

const data = await response.json();
console.log(data.response);
```

## 🛠️ Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Start the API server
python web_api.py

# API will be available at http://localhost:8000
```

## 🚂 Railway Deployment

This project is optimized for Railway deployment:

1. **Connect GitHub repo** to Railway
2. **Set environment variables**:
   ```
   INTERSECT_API_KEY=your-secure-api-key
   OLLAMA_URL=your-ollama-instance-url
   OLLAMA_MODEL=llama3.1
   ALLOWED_ORIGINS=https://yourdomain.com
   ```
3. **Deploy** - builds in 2-3 minutes with Nixpacks

## 📊 Dataset Information

- **30 total conversations** covering comprehensive topics
- **Categories**: Introduction, skills, services, certifications, experience, CTF hints
- **Optimized responses** for natural conversation flow
- **Easter eggs** for engagement and personality

## 🔒 Security Features

- Rate limiting (configurable per IP)
- CORS protection for website integration
- Optional API key authentication
- Input validation and sanitization
- Comprehensive error handling

## 🎯 Key Topics Covered

- Cybersecurity expertise and certifications
- Application security services
- TamperTantrum Labs business
- Personal journey (mom of 3, career change)
- Technical skills (Burp Suite, OWASP ZAP, etc.)
- CTF challenges and hints

## 📞 Support

For questions about Brenda's services:
- Email: hensley.brenda@protonmail.com
- Website: https://tampertantrumlabs.com

---

Built with ❤️ for cybersecurity professionals and potential clients.
python setup_ollama.py test
```

## Troubleshooting

**Ollama not connecting?**
- Make sure Ollama is installed and running
- Check if the service is on http://localhost:11434
- Try restarting: `ollama serve`

**Model not found?**
- Pull the model: `ollama pull llama3.1`
- Check available models: `ollama list`

**Slow responses?**
- Try a smaller model like `llama2`
- Ensure your computer has enough RAM (8GB+ recommended)

## Next Steps

This chatbot can be:
- Embedded in a website using a web framework
- Deployed to a server for 24/7 availability
- Extended with more conversation data
- Connected to other AI services

# 🚂 Railway Deployment Guide for The Intersect

This guide will help you deploy your chatbot API to Railway with all the necessary configurations.

## 📋 Prerequisites

1. **Railway Account**: Sign up at [railway.app](https://railway.app)
2. **GitHub Repository**: Your code needs to be in a GitHub repo
3. **Ollama Instance**: You'll need Ollama running somewhere accessible

## 🚀 Deployment Steps

### Step 1: Prepare Your Repository

1. **Push your code to GitHub**:
```bash
git add .
git commit -m "Add Railway deployment configuration"
git push origin main
```

2. **Verify required files exist**:
   - ✅ `railway.toml` - Railway configuration
   - ✅ `requirements.txt` - Python dependencies
   - ✅ `web_api.py` - Your main application
   - ✅ `portfolio_dataset.json` - Chatbot data

### Step 2: Deploy to Railway

1. **Connect GitHub to Railway**:
   - Go to [railway.app](https://railway.app)
   - Click "Start a New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository

2. **Railway will automatically**:
   - Detect it's a Python project
   - Install dependencies from `requirements.txt`
   - Use the start command from `railway.toml`

### Step 3: Configure Environment Variables

In your Railway dashboard, go to **Variables** and add:

```bash
# Required
INTERSECT_API_KEY=your-super-secure-api-key-here
OLLAMA_URL=https://your-ollama-instance-url.com
OLLAMA_MODEL=llama3.1

# Optional (with defaults)
RATE_LIMIT_REQUESTS=20
RATE_LIMIT_WINDOW=60
ALLOWED_ORIGINS=https://tampertantrumlabs.com,https://www.tampertantrumlabs.com
LOG_LEVEL=info
```

### Step 4: Set Up Ollama

**Option A: Deploy Ollama to Railway (Recommended)**

1. Create a new Railway service for Ollama:
```bash
# In Railway dashboard, create new service
# Use Docker deploy with image: ollama/ollama:latest
```

2. Set Ollama environment variables:
```bash
OLLAMA_HOST=0.0.0.0
```

3. Add volume for model storage:
   - Go to service settings
   - Add volume: `/root/.ollama`

4. Pull your model:
```bash
# SSH into Ollama service or use Railway CLI
ollama pull llama3.1
```

**Option B: Use External Ollama**
- Deploy Ollama on another cloud service
- Update `OLLAMA_URL` to point to your instance

### Step 5: Configure Domain (Optional)

1. **Custom Domain**:
   - Go to service **Settings**
   - Click **Domains**
   - Add your custom domain
   - Update DNS records as instructed

2. **HTTPS**: Railway provides automatic HTTPS

## 🔧 Configuration Files Explained

### `railway.toml`
```toml
[build]
builder = "NIXPACKS"  # Railway's auto-detection

[deploy]
startCommand = "python -m uvicorn web_api:app --host 0.0.0.0 --port $PORT"
healthcheckPath = "/api/v1/health"
healthcheckTimeout = 300
```

### Environment Variables
- `PORT`: Automatically set by Railway
- `RAILWAY_ENVIRONMENT`: Set to "production"
- Your custom variables (API keys, etc.)

## 🌐 After Deployment

### 1. Test Your API
Your API will be available at: `https://your-service-name.railway.app`

Test endpoints:
- Health: `GET /api/v1/health`
- Chat: `POST /api/v1/chat`
- Docs: `GET /docs`

### 2. Update Website Integration
Update your website's API URL:
```javascript
const intersect = new IntersectSDK('https://your-service-name.railway.app');
```

### 3. Monitor Your Service
- Check logs in Railway dashboard
- Monitor health endpoint
- Set up alerts if needed

## 💰 Railway Pricing

- **Hobby Plan**: $5/month with generous limits
- **Pro Plan**: Pay-as-you-use for heavy traffic
- **Free Tier**: Limited but good for testing

## 🛠️ Troubleshooting

### Common Issues:

**1. Build Failures**
```bash
# Check requirements.txt includes all dependencies
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
pydantic>=2.4.0
requests>=2.28.0
```

**2. Port Issues**
- Railway sets `PORT` environment variable
- Make sure your app uses `os.getenv("PORT", "8000")`

**3. Ollama Connection**
```bash
# Test Ollama URL in Railway logs
curl $OLLAMA_URL/api/tags
```

**4. CORS Issues**
```bash
# Make sure ALLOWED_ORIGINS includes your website domain
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

### Viewing Logs:
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and view logs
railway login
railway logs
```

## 🔄 Continuous Deployment

Railway automatically redeploys when you push to your main branch:

```bash
git add .
git commit -m "Update chatbot responses"
git push origin main
# 🚂 Railway will automatically redeploy!
```

## 📊 Monitoring

### Built-in Health Checks
Railway monitors `/api/v1/health` automatically

### Custom Monitoring
Add monitoring services like:
- **UptimeRobot**: Free uptime monitoring
- **Pingdom**: Comprehensive monitoring
- **DataDog**: Full observability stack

## 🚀 Advanced Configuration

### Auto-scaling
Railway can auto-scale based on traffic. Configure in service settings.

### Custom Build Commands
```toml
# In railway.toml
[build]
buildCommand = "pip install -r requirements.txt && python setup_custom.py"
```

### Database Integration
If you need a database later:
```bash
# Railway provides managed databases
# PostgreSQL, MySQL, MongoDB, Redis
```

## 🎯 Final Checklist

Before going live:

- [ ] ✅ API key is secure and unique
- [ ] ✅ CORS origins match your website domain
- [ ] ✅ Ollama is accessible and model is loaded
- [ ] ✅ Health check returns 200 OK
- [ ] ✅ Test chat endpoint with real messages
- [ ] ✅ Rate limiting is appropriate for your traffic
- [ ] ✅ Custom domain configured (if using)
- [ ] ✅ Website integration updated with new URL

## 🎉 You're Live!

Your chatbot API is now running on Railway with:
- ⚡ Fast global CDN
- 🔒 Automatic HTTPS
- 📊 Built-in monitoring
- 🔄 Auto-deployments from GitHub
- 💾 Persistent storage for Ollama models

Your users can now chat with The Intersect directly from your website! 🤖

---

**Need help?** Check Railway's [documentation](https://docs.railway.app) or their Discord community.

# Simple FastAPI Dockerfile for Railway
# No more Ollama - just clean, fast API!

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE $PORT

# Start FastAPI directly
CMD uvicorn web_api:app --host 0.0.0.0 --port ${PORT:-8000}
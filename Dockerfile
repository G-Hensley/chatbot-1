# Simple FastAPI Dockerfile for Railway
# No more Ollama - just clean, fast API!

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Update pip and install dependencies with no cache
RUN pip install --upgrade pip

# Copy requirements and install with no cache and upgrade all
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE $PORT

# Start FastAPI directly
CMD uvicorn web_api:app --host 0.0.0.0 --port ${PORT:-8000}
# Brenda's Portfolio Chatbot

A chatbot trained on Brenda Hensley's portfolio information, designed to answer questions about her background, skills, and services.

## Quick Start with Ollama

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Setup Ollama
```bash
python setup_ollama.py
```

This will:
- Check if Ollama is installed
- Start the Ollama service
- Download the llama3.1 model
- Test the connection

### 3. Start Chatting
```bash
python ollama_chatbot.py
```

## Manual Ollama Setup

If the automatic setup doesn't work:

1. **Install Ollama**
   - Visit: https://ollama.ai
   - Download and install for your OS

2. **Start Ollama Service**
   ```bash
   ollama serve
   ```

3. **Pull a Model**
   ```bash
   ollama pull llama3.1
   ```

4. **Run the Chatbot**
   ```bash
   python ollama_chatbot.py
   ```

## Alternative Models

You can use different models by editing `ollama_chatbot.py`:

```python
# Popular options:
chatbot = OllamaPortfolioChatbot(model_name="llama3.1")      # Default
chatbot = OllamaPortfolioChatbot(model_name="llama2")        # Smaller
chatbot = OllamaPortfolioChatbot(model_name="mistral")       # Fast
chatbot = OllamaPortfolioChatbot(model_name="codellama")     # Code-focused
```

## Dataset Information

- **Total Conversations**: 31
- **Categories**: Background, skills, services, certifications, experience, and more
- **Format**: JSON with question-answer pairs

### Key Topics Covered:
- Early tech curiosity and background
- Educational journey (6-month degree while pregnant)
- Certifications (Security+, CySA+, PenTest+, etc.)
- Motherhood and career balance
- Application security expertise
- TamperTantrum Labs business

## Customizing the Dataset

To add more conversations:

```python
from dataset_manager import PortfolioDatasetManager

manager = PortfolioDatasetManager()
manager.add_conversation("category", "Question?", "Answer response")
manager.save_dataset()
```

## Files Overview

- `portfolio_dataset.json` - Main conversation dataset
- `dataset_manager.py` - Tools for managing the dataset
- `ollama_chatbot.py` - Main chatbot with Ollama integration
- `setup_ollama.py` - Automatic setup script
- `portfolio_trainer.py` - For training custom models (alternative to Ollama)

## Testing

Test the setup:
```bash
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

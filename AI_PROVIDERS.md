# 🤖 AI Providers Guide

Complete guide to using multiple AI providers in your AI Notebook System.

## 🎯 Overview

Your AI Notebook System supports three powerful AI providers:

1. **🤖 Ollama (Local)** - Default, private, fast
2. **🌐 OpenAI** - Enterprise-grade, high-quality
3. **🔮 Google Gemini** - Advanced reasoning, cost-effective

## 🚀 Quick Start

### 1. Default Setup (Ollama)
```bash
# Ollama runs automatically with Docker
# No API keys needed
# Models downloaded automatically

# Check if Ollama is running
curl http://localhost:11434/api/tags

# Start using AI immediately!
```

### 2. Enable Cloud Providers (Optional)
```bash
# Add to .env file
OPENAI_API_KEY=your_openai_key_here
GEMINI_API_KEY=your_gemini_key_here

# Restart services
docker-compose restart backend
```

## 🤖 Ollama (Local) - Default Provider

### Why Ollama?
- ✅ **Privacy**: All data stays on your machine
- ✅ **Speed**: No network latency
- ✅ **Cost**: Free, no API charges
- ✅ **Offline**: Works without internet
- ✅ **Customizable**: Download any model you want

### Available Models
```bash
# Check installed models
curl http://localhost:11434/api/tags

# Download additional models
ollama pull codellama:7b      # Code generation
ollama pull mistral:7b        # General purpose
ollama pull llama3.2:8b       # Balanced performance
ollama pull neural-chat:7b    # Conversations
```

### Model Recommendations
| Use Case | Recommended Model | Size | Performance |
|----------|------------------|------|-------------|
| **Code Generation** | `codellama:7b` | 7B | ⭐⭐⭐⭐⭐ |
| **General Tasks** | `llama3.2:3b` | 3B | ⭐⭐⭐⭐ |
| **High Quality** | `llama3.2:8b` | 8B | ⭐⭐⭐⭐⭐ |
| **Conversations** | `neural-chat:7b` | 7B | ⭐⭐⭐⭐ |

### Ollama Management
```bash
# Start Ollama service
docker-compose up -d ollama

# View logs
docker-compose logs -f ollama

# Restart Ollama
docker-compose restart ollama

# Stop Ollama
docker-compose stop ollama
```

## 🌐 OpenAI - Enterprise AI

### Why OpenAI?
- ✅ **Quality**: Industry-leading AI models
- ✅ **Reliability**: 99.9% uptime SLA
- ✅ **Features**: Advanced reasoning, code generation
- ✅ **Integration**: Extensive API ecosystem

### Setup
```bash
# 1. Get API key from https://platform.openai.com/
# 2. Add to .env file
OPENAI_API_KEY=sk-your-key-here

# 3. Restart backend
docker-compose restart backend
```

### Available Models
- **GPT-4.1-mini**: Fast, cost-effective
- **GPT-4**: High quality, reasoning
- **GPT-3.5-turbo**: Balanced performance

### Usage Examples
```python
# Generate code with OpenAI
response = await ai_provider_service.generate_response(
    prompt="Create a pandas function to clean data",
    provider=AIProvider.OPENAI,
    model="gpt-4"
)

# Analyze errors with OpenAI
response = await ai_provider_service.generate_response(
    prompt="Fix this Python error: ...",
    provider=AIProvider.OPENAI
)
```

## 🔮 Google Gemini - Advanced Reasoning

### Why Gemini?
- ✅ **Reasoning**: Advanced logical thinking
- ✅ **Cost**: Competitive pricing
- ✅ **Multimodal**: Text, code, images
- ✅ **Performance**: Fast response times

### Setup
```bash
# 1. Get API key from https://makersuite.google.com/
# 2. Add to .env file
GEMINI_API_KEY=your_gemini_key_here

# 3. Restart backend
docker-compose restart backend
```

### Available Models
- **gemini-1.5-pro**: High quality, reasoning
- **gemini-1.5-flash**: Fast, efficient
- **gemini-pro**: General purpose

### Usage Examples
```python
# Optimize workflows with Gemini
response = await ai_provider_service.generate_response(
    prompt="Optimize this data pipeline",
    provider=AIProvider.GEMINI,
    model="gemini-1.5-pro"
)

# Get explanations with Gemini
response = await ai_provider_service.generate_response(
    prompt="Explain this machine learning concept",
    provider=AIProvider.GEMINI
)
```

## 🔄 Provider Switching

### Automatic Fallback
The system automatically falls back to available providers if your preferred one fails:

```python
# Try OpenAI first, fallback to Ollama
try:
    response = await ai_provider_service.generate_response(
        prompt="Your prompt",
        provider=AIProvider.OPENAI
    )
except Exception:
    # Automatically falls back to Ollama
    response = await ai_provider_service.generate_response(
        prompt="Your prompt",
        provider=AIProvider.OLLAMA
    )
```

### Manual Provider Selection
```python
# Always use specific provider
response = await ai_provider_service.generate_response(
    prompt="Your prompt",
    provider=AIProvider.OLLAMA  # Force Ollama
)

# Use default provider
response = await ai_provider_service.generate_response(
    prompt="Your prompt"
    # Uses DEFAULT_AI_PROVIDER from config
)
```

### Dynamic Provider Switching
```python
# Switch default provider at runtime
await ai_provider_service.switch_default_provider(AIProvider.OPENAI)

# Now all requests use OpenAI by default
response = await ai_provider_service.generate_response("Your prompt")
```

## 📊 Provider Comparison

| Feature | Ollama | OpenAI | Gemini |
|---------|--------|--------|--------|
| **Privacy** | 🔒 Full | 🌐 Cloud | 🌐 Cloud |
| **Cost** | 💰 Free | 💰 Per-token | 💰 Per-token |
| **Speed** | ⚡ Fast | 🚀 Very Fast | 🚀 Very Fast |
| **Quality** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Offline** | ✅ Yes | ❌ No | ❌ No |
| **Customization** | ✅ Full | ❌ Limited | ❌ Limited |

## 🎯 Use Case Recommendations

### Use Ollama When:
- 🔒 Privacy is critical
- 💰 Budget is limited
- ⚡ Speed is important
- 🌐 Internet is unreliable
- 🧪 Experimenting with models

### Use OpenAI When:
- 🎯 Quality is paramount
- 🏢 Enterprise features needed
- 🔄 Reliability is critical
- 📊 Advanced reasoning required
- 💼 Professional workflows

### Use Gemini When:
- 🧠 Advanced reasoning needed
- 💰 Cost optimization important
- 🚀 Fast responses required
- 🔍 Analysis and insights
- 📈 Performance optimization

## 🛠️ Configuration Options

### Environment Variables
```bash
# AI Provider Configuration
DEFAULT_AI_PROVIDER=ollama          # Default provider
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_DEFAULT_MODEL=llama3.2:3b
OLLAMA_TIMEOUT=120
OLLAMA_MAX_TOKENS=4000
OLLAMA_TEMPERATURE=0.7

OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-4.1-mini
OPENAI_MAX_TOKENS=4000
OPENAI_TEMPERATURE=0.7
OPENAI_BASE_URL=https://api.openai.com/v1

GEMINI_API_KEY=your_key_here
GEMINI_MODEL=gemini-1.5-pro
GEMINI_MAX_TOKENS=4000
GEMINI_TEMPERATURE=0.7
```

### Runtime Configuration
```python
# Change provider settings at runtime
from app.services.ai_provider_service import ai_provider_service

# Switch default provider
await ai_provider_service.switch_default_provider(AIProvider.OPENAI)

# Get provider status
providers = await ai_provider_service.get_available_providers()
health = await ai_provider_service.health_check()
```

## 🔍 Monitoring & Debugging

### Check Provider Health
```bash
# API endpoint
curl http://localhost:8000/api/v1/ai/health

# Response format
{
  "success": true,
  "health_status": {
    "ollama": {"available": true, "healthy": true},
    "openai": {"available": false, "healthy": false},
    "gemini": {"available": true, "healthy": true}
  }
}
```

### View Available Providers
```bash
# API endpoint
curl http://localhost:8000/api/v1/ai/providers

# Response format
{
  "success": true,
  "providers": [
    {
      "provider": "ollama",
      "available": true,
      "healthy": true,
      "is_default": true
    }
  ]
}
```

### Debug Provider Issues
```bash
# Check Ollama logs
docker-compose logs -f ollama

# Check backend logs
docker-compose logs -f backend

# Test Ollama directly
curl http://localhost:11434/api/tags

# Test OpenAI (if configured)
curl -H "Authorization: Bearer $OPENAI_API_KEY" \
     https://api.openai.com/v1/models
```

## 🚀 Advanced Usage

### Custom Prompts
```python
# Create specialized prompts for different providers
ollama_prompt = "You are a Python expert. Write code for: {request}"
openai_prompt = "As an AI coding assistant, generate: {request}"
gemini_prompt = "You are a data science expert. Create: {request}"

# Use provider-specific prompts
if provider == AIProvider.OLLAMA:
    prompt = ollama_prompt.format(request=user_request)
elif provider == AIProvider.OPENAI:
    prompt = openai_prompt.format(request=user_request)
```

### Model Selection
```python
# Choose specific models for different tasks
code_generation = {
    AIProvider.OLLAMA: "codellama:7b",
    AIProvider.OPENAI: "gpt-4",
    AIProvider.GEMINI: "gemini-1.5-pro"
}

# Use appropriate model for task
model = code_generation.get(provider, "default")
response = await ai_provider_service.generate_response(
    prompt=prompt,
    provider=provider,
    model=model
)
```

### Batch Processing
```python
# Process multiple requests with different providers
requests = [
    {"prompt": "Generate code", "provider": AIProvider.OLLAMA},
    {"prompt": "Analyze data", "provider": AIProvider.OPENAI},
    {"prompt": "Optimize workflow", "provider": AIProvider.GEMINI}
]

responses = []
for req in requests:
    response = await ai_provider_service.generate_response(
        prompt=req["prompt"],
        provider=req["provider"]
    )
    responses.append(response)
```

## 🎉 Best Practices

### 1. **Start with Ollama**
- Use Ollama for development and testing
- No API costs or rate limits
- Fast iteration and experimentation

### 2. **Add Cloud Providers Gradually**
- Start with one cloud provider
- Test performance and quality
- Add more as needed

### 3. **Use Provider Strengths**
- Ollama: Privacy, speed, cost
- OpenAI: Quality, reliability
- Gemini: Reasoning, analysis

### 4. **Monitor Usage**
- Track provider performance
- Monitor costs (cloud providers)
- Optimize based on results

### 5. **Plan for Fallbacks**
- Always have Ollama as backup
- Test fallback scenarios
- Ensure smooth transitions

## 🆘 Troubleshooting

### Common Issues

**Ollama not responding:**
```bash
# Check if running
docker-compose ps ollama

# Restart service
docker-compose restart ollama

# Check logs
docker-compose logs ollama
```

**OpenAI API errors:**
```bash
# Verify API key
echo $OPENAI_API_KEY

# Check quota
curl -H "Authorization: Bearer $OPENAI_API_KEY" \
     https://api.openai.com/v1/usage
```

**Gemini not working:**
```bash
# Verify API key
echo $GEMINI_API_KEY

# Check API status
curl https://generativelanguage.googleapis.com/v1beta/models
```

### Performance Optimization

**For Ollama:**
- Use smaller models for speed
- Increase timeout for complex tasks
- Monitor memory usage

**For Cloud Providers:**
- Use appropriate model sizes
- Implement caching
- Batch requests when possible

## 🎯 Next Steps

1. **Start with Ollama**: Get familiar with local AI
2. **Add OpenAI**: For high-quality results
3. **Add Gemini**: For advanced reasoning
4. **Customize**: Adjust models and prompts
5. **Optimize**: Monitor and improve performance

---

🚀 **Your multi-provider AI system is ready! Start building amazing AI-powered workflows today!** 
# Ollama Local LLM Integration Guide

## Overview
Your JIRA Ticket Generator now supports **Ollama** for running local LLMs like Llama 3! This allows you to:
- ✅ Run everything locally without API costs
- ✅ Keep your data private
- ✅ Test performance of open-source models like Llama 3:8b
- ✅ Compare local vs cloud LLM quality

## Quick Start

### 1. Install Ollama

**macOS/Linux:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

**Windows:**
Download from https://ollama.com/download

**Verify Installation:**
```bash
ollama --version
```

### 2. Download Llama 3 Model

```bash
# Download Llama 3 8B (recommended for testing)
ollama pull llama3:8b

# Or download Llama 3 70B (more powerful, requires more RAM)
ollama pull llama3:70b

# Other available models:
ollama pull mistral        # Fast and efficient
ollama pull codellama      # Optimized for code
ollama pull llama2         # Previous generation
```

**Check Downloaded Models:**
```bash
ollama list
```

### 3. Start Ollama Server

Ollama runs as a background service on port 11434:

```bash
# Usually starts automatically, but you can manually start:
ollama serve
```

**Verify Server Running:**
```bash
curl http://localhost:11434/api/version
```

### 4. Configure JIRA Ticket Generator

Edit your `.env` file:

```bash
# Change LLM_PROVIDER to ollama
LLM_PROVIDER=ollama

# Set Ollama configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3:8b
```

**Full .env Example:**
```env
# Jira Configuration
JIRA_URL=https://your-domain.atlassian.net/
JIRA_EMAIL=your-email@example.com
JIRA_API_TOKEN=your-api-token

# LLM Configuration - USE OLLAMA
LLM_PROVIDER=ollama

# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3:8b

# Application Settings
DEFAULT_PROJECT_KEY=PROJ
```

### 5. Test It!

```bash
# Start the backend
python3 app.py

# In another terminal, test with the CLI
python3 jira_gen.py "Create a user authentication system with JWT tokens"
```

## Model Comparison

### Llama 3 8B (Recommended for Testing)
- **Size**: ~4.7GB
- **RAM**: 8GB minimum
- **Speed**: Fast (~15-30 tokens/sec on M1/M2)
- **Quality**: Good for most tasks
- **Use Case**: Development, testing, general use

### Llama 3 70B (High Quality)
- **Size**: ~40GB
- **RAM**: 64GB recommended
- **Speed**: Slower (~5-10 tokens/sec)
- **Quality**: Excellent, comparable to GPT-4
- **Use Case**: Production, complex tasks

### Mistral 7B (Alternative)
- **Size**: ~4.1GB
- **RAM**: 8GB minimum
- **Speed**: Very fast (~20-40 tokens/sec)
- **Quality**: Good, efficient
- **Use Case**: Quick iterations, resource-constrained environments

### CodeLlama (Code-Specialized)
- **Size**: ~3.8GB
- **RAM**: 8GB minimum
- **Speed**: Fast
- **Quality**: Better for code-related tasks
- **Use Case**: Technical documentation, code analysis

## Switching Between Providers

You can easily switch between OpenAI, Claude, and Ollama:

```bash
# Use OpenAI (cloud, fast, high quality, $$$)
LLM_PROVIDER=openai
LLM_MODEL=gpt-4-turbo

# Use Anthropic Claude (cloud, high quality, $$$)
LLM_PROVIDER=anthropic
LLM_MODEL=claude-3-opus-20240229

# Use Ollama (local, free, private)
LLM_PROVIDER=ollama
OLLAMA_MODEL=llama3:8b
```

Just change the `.env` and restart the backend!

## Performance Tips

### Speed Optimization
1. **Use GPU acceleration** (if available):
   ```bash
   # Ollama automatically uses GPU if CUDA/Metal is available
   # Check GPU usage: nvidia-smi (NVIDIA) or Activity Monitor (Mac)
   ```

2. **Use smaller models** for development:
   ```bash
   ollama pull llama3:8b  # Faster
   # vs
   ollama pull llama3:70b # Slower but better
   ```

3. **Keep Ollama warm**:
   ```bash
   # Make a test call to keep model in memory
   curl -X POST http://localhost:11434/api/generate -d '{
     "model": "llama3:8b",
     "prompt": "Test",
     "stream": false
   }'
   ```

### Quality Optimization
1. **Use larger models** for production:
   ```bash
   OLLAMA_MODEL=llama3:70b
   ```

2. **Adjust temperature** in code (already set to 0.3 for consistency)

3. **Use specialized models** for specific tasks:
   - CodeLlama for technical tasks
   - Mistral for general tasks
   - Llama 3 70B for complex requirements

## Troubleshooting

### Problem: "Connection refused" to localhost:11434
**Solution:**
```bash
# Check if Ollama is running
ps aux | grep ollama

# Start Ollama if not running
ollama serve

# Check port is accessible
curl http://localhost:11434/api/version
```

### Problem: "Model not found"
**Solution:**
```bash
# List available models
ollama list

# Pull the model specified in .env
ollama pull llama3:8b
```

### Problem: "Out of memory"
**Solution:**
1. Use a smaller model:
   ```bash
   OLLAMA_MODEL=mistral  # or llama3:8b instead of llama3:70b
   ```

2. Close other applications

3. Check system resources:
   ```bash
   # macOS/Linux
   free -h  # or top

   # Windows
   Task Manager → Performance
   ```

### Problem: Slow performance
**Solution:**
1. Use smaller model (llama3:8b vs llama3:70b)
2. Check CPU/GPU usage
3. Ensure Ollama is using GPU:
   ```bash
   # Mac: Check Metal usage in Activity Monitor
   # Linux: nvidia-smi for NVIDIA GPUs
   ```

4. Close other memory-intensive applications

### Problem: JSON parsing errors
**Cause:** Ollama models may not always return perfect JSON

**Solution:** The code already handles this with fallback to simple extraction:
```python
except json.JSONDecodeError:
    return self._extract_simple(text, project_key)
```

If you get frequent JSON errors, try:
1. Using `llama3:70b` (better instruction following)
2. Switching to OpenAI/Claude temporarily for comparison
3. Checking Ollama logs: `ollama logs`

## Comparing LLM Quality

### Test Script
Create `compare_llms.sh`:

```bash
#!/bin/bash

# Test input
TEST_INPUT="Create a user authentication system with login, registration, and password reset features"

echo "=== Testing OpenAI ==="
sed -i '' 's/LLM_PROVIDER=.*/LLM_PROVIDER=openai/' .env
python3 jira_gen.py "$TEST_INPUT" > output_openai.md

echo "=== Testing Claude ==="
sed -i '' 's/LLM_PROVIDER=.*/LLM_PROVIDER=anthropic/' .env
python3 jira_gen.py "$TEST_INPUT" > output_claude.md

echo "=== Testing Ollama Llama3 ==="
sed -i '' 's/LLM_PROVIDER=.*/LLM_PROVIDER=ollama/' .env
python3 jira_gen.py "$TEST_INPUT" > output_ollama.md

echo "Compare outputs:"
echo "- output_openai.md"
echo "- output_claude.md"
echo "- output_ollama.md"
```

### Quality Metrics to Compare
1. **Completeness**: Does it extract all epics/tasks?
2. **Detail Level**: Are acceptance criteria comprehensive?
3. **Technical Accuracy**: Are technical details correct?
4. **Structure**: Is the markdown well-formatted?
5. **Missing Tasks**: Does it suggest error handling, testing, etc.?

## Cost Comparison

### OpenAI GPT-4 Turbo
- **Cost**: ~$10-20/1M tokens input, ~$30-60/1M tokens output
- **Typical request**: ~$0.05-0.10 per generation
- **Monthly (100 requests)**: ~$5-10

### Anthropic Claude Opus
- **Cost**: ~$15/1M tokens input, ~$75/1M tokens output
- **Typical request**: ~$0.08-0.15 per generation
- **Monthly (100 requests)**: ~$8-15

### Ollama (Local)
- **Cost**: **$0** (FREE!)
- **Requirements**: Computer with 8GB+ RAM
- **One-time setup**: 5-10 minutes

## Advanced Configuration

### Multiple Ollama Instances
Run different models on different ports:

```bash
# Terminal 1: Llama 3 8B on port 11434
OLLAMA_HOST=0.0.0.0:11434 ollama serve

# Terminal 2: Llama 3 70B on port 11435
OLLAMA_HOST=0.0.0.0:11435 ollama serve
```

Update `.env`:
```bash
OLLAMA_BASE_URL=http://localhost:11435  # Use the 70B model
```

### Custom Models
Fine-tune your own model:

```bash
# Create Modelfile
cat > Modelfile << EOF
FROM llama3:8b
PARAMETER temperature 0.3
PARAMETER top_p 0.9
SYSTEM You are a JIRA ticket expert specialized in technical requirements.
EOF

# Create custom model
ollama create jira-expert -f Modelfile

# Use it
OLLAMA_MODEL=jira-expert
```

### Remote Ollama Server
Run Ollama on a powerful server, use from laptop:

**Server:**
```bash
OLLAMA_HOST=0.0.0.0:11434 ollama serve
```

**Laptop .env:**
```bash
OLLAMA_BASE_URL=http://server-ip:11434
```

## Integration Details

### How It Works
The integration uses Ollama's OpenAI-compatible API:

```python
# config.py
if cls.llm_provider == 'ollama':
    from openai import OpenAI
    return OpenAI(
        base_url=cls.ollama_base_url + '/v1',
        api_key='ollama'  # Dummy key, not validated
    )
```

### Code Changes Made
1. **config.py**: Added Ollama provider support
2. **extraction_agent.py**: Model selection based on provider
3. **review_agent.py**: Model selection based on provider
4. **.env**: Added OLLAMA_BASE_URL and OLLAMA_MODEL

### API Compatibility
Ollama implements OpenAI's chat completions API:
- ✅ Chat completions
- ✅ Streaming
- ✅ System messages
- ⚠️ No `response_format={"type": "json_object"}` (handled gracefully)

## Next Steps

1. **Install Ollama**: `curl -fsSL https://ollama.com/install.sh | sh`
2. **Download Llama 3**: `ollama pull llama3:8b`
3. **Update .env**: Set `LLM_PROVIDER=ollama`
4. **Test it**: Run `python3 app.py` and try generating tickets
5. **Compare quality**: Try the same input with OpenAI, Claude, and Ollama
6. **Share results**: Let me know how Llama 3 performs! 🚀

## Resources

- **Ollama Docs**: https://github.com/ollama/ollama
- **Ollama Models**: https://ollama.com/library
- **Llama 3 Info**: https://llama.meta.com/llama3/
- **OpenAI API Compatibility**: https://github.com/ollama/ollama/blob/main/docs/openai.md

## Questions?

Feel free to ask if you need help with:
- Installing Ollama
- Choosing the right model
- Performance optimization
- Quality comparison
- Custom model creation

**Enjoy your local LLM! 🦙**

# Quick Start Guide - AI Study Assistant

## Installation Steps

### 1. Install Python (if not already installed)
- Download Python 3.8+ from [python.org](https://python.org)
- During installation, check "Add Python to PATH"

### 2. Install OLLAMA

**For Core i3 Laptop - Recommended Setup:**

1. Download OLLAMA from: https://ollama.ai/download
2. Install OLLAMA (Windows installer)
3. Open Command Prompt and run:
   ```bash
   ollama pull phi3:mini
   ```

**Alternative for even slower systems:**
```bash
ollama pull llama3.2:1b
```

**Verify installation:**
```bash
ollama list
```

### 3. Setup the Study Assistant

Open Command Prompt in the project folder and run:

```bash
# Run the setup script
python setup.py
```

The setup script will:
- ✅ Check Python version
- ✅ Install required packages
- ✅ Check OLLAMA installation
- ✅ Verify model availability
- ✅ Create necessary directories
- ✅ Create configuration files

### 4. Configure (Optional)

Edit `.env` file if needed:
```
OLLAMA_MODEL=phi3:mini     # Or llama3.2:1b for lighter model
OLLAMA_HOST=http://localhost:11434
LOG_LEVEL=INFO
```

## Running the Application

### Method 1: Web Interface (Recommended)

```bash
python main.py
```

Then open your browser to: **http://localhost:8501**

### Method 2: Demo Mode

```bash
python demo.py
```

Choose option to see:
- Basic usage examples
- Design patterns demonstration
- Both

## Using the Study Assistant

### Basic Usage

1. Open the web interface
2. Type your question in the chat box
3. Get guidance (not direct answers!)

### Example Interactions

**❌ Wrong Approach:**
> "What is the answer to 2x + 5 = 15?"

**✅ Better Approach:**
> "I don't understand how to solve 2x + 5 = 15. Can you help me?"

**Response:** You'll get guiding questions like:
- "What operation is being performed on x?"
- "What would you need to do to isolate x?"
- "What's the opposite of adding 5?"

### Getting Hints

If you're stuck, you can:
- Type "hint" in the chat
- Click "Request Hint" button in sidebar
- Get up to 3 progressive hints

### Understanding the Interface

**Main Chat:**
- Type questions naturally
- See your conversation history
- Get strategy badges showing approach used

**Sidebar:**
- Connection status
- Session statistics
- Quick actions
- Learning tips

## Tips for Best Learning

1. **Ask Open Questions**: "I don't understand X" instead of "What is X?"
2. **Engage with Guiding Questions**: Think about the questions asked
3. **Use Hints Wisely**: Try to think before asking for hints
4. **Focus on Understanding**: Not just getting answers
5. **Break Down Problems**: Ask about concepts, not full solutions

## Troubleshooting

### OLLAMA not connecting

**Check if OLLAMA is running:**
```bash
ollama list
```

**If not working:**
1. Restart OLLAMA service
2. Check Windows Services for "OLLAMA"
3. Run: `ollama serve` in a terminal

### Model not found

```bash
ollama pull phi3:mini
```

### Python packages missing

```bash
pip install -r requirements.txt
```

### Web interface not loading

1. Check if port 8501 is available
2. Try: `python main.py` again
3. Check firewall settings

### Slow responses

**For Core i3 laptops:**

1. Use lighter model:
   ```bash
   ollama pull llama3.2:1b
   ```

2. Update `.env`:
   ```
   OLLAMA_MODEL=llama3.2:1b
   MAX_CONTEXT_LENGTH=1024
   ```

3. Close other applications
4. Ensure OLLAMA has enough RAM (4GB minimum)

## System Requirements

**Minimum:**
- Processor: Core i3 or equivalent
- RAM: 4GB
- Storage: 5GB free space
- OS: Windows 10/11, Linux, macOS

**Recommended:**
- Processor: Core i5 or better
- RAM: 8GB
- Storage: 10GB free space
- Internet: For initial model download

## OLLAMA Model Comparison

| Model | Size | Speed on i3 | Quality | Recommended For |
|-------|------|-------------|---------|----------------|
| phi3:mini | 3.8GB | Medium | Good | **Most users** |
| llama3.2:1b | 1.3GB | Fast | Fair | Slow systems |
| llama3:8b | 4.7GB | Slow | Better | i5+ systems |

## Features

✅ **Socratic Learning**: Guides through questions
✅ **Progressive Hints**: 3 levels of hints
✅ **Concept Explanation**: Explains without solving
✅ **Problem Decomposition**: Breaks down complex problems
✅ **Progress Tracking**: Monitors your learning
✅ **Session Statistics**: See your learning patterns

## What It Won't Do

❌ Solve homework directly
❌ Give test answers
❌ Do your work for you
❌ Provide copy-paste solutions

## What It Will Do

✅ Help you understand concepts
✅ Guide you to discover answers
✅ Explain underlying principles
✅ Build problem-solving skills
✅ Support your learning journey

## Getting Help

### Application Issues
1. Check `data/app.log` for errors
2. Run `python setup.py` again
3. Verify OLLAMA is running

### Learning Questions
- Use the built-in help command: type "help"
- Refer to examples in demo mode
- Read the tips in the sidebar

## Example Session

```
You: Hello!
Assistant: Hi! I'm your AI Study Assistant! I'm here to help you LEARN...

You: I don't understand photosynthesis
Assistant: Great question! Let me help you understand this concept...
[Asks guiding questions about plants, energy, etc.]

You: hint
Assistant: [Provides first hint about sunlight and energy conversion]

You: [Continues conversation...]
```

## Next Steps

1. **Start with simple questions** to get comfortable
2. **Try different subjects** to see various strategies
3. **Use the hint system** when genuinely stuck
4. **Check your statistics** to see progress
5. **Experiment with learning styles**

## Commands Reference

| Command | Description |
|---------|-------------|
| `python main.py` | Start web interface |
| `python demo.py` | Run demo mode |
| `python setup.py` | Run setup/verification |
| `ollama list` | List installed models |
| `ollama pull phi3:mini` | Download model |
| `ollama serve` | Start OLLAMA service |

## Support

For issues or questions:
1. Check `DEVELOPER_GUIDE.md` for technical details
2. Review `data/app.log` for errors
3. Ensure OLLAMA is properly configured
4. Verify Python dependencies are installed

---

**Ready to learn? Run `python main.py` and start your learning journey! 🎓**

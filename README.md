# AI Study Assistant Chatbot

An intelligent study assistant that helps students learn through guided questioning rather than providing direct answers.

## Features

- **Socratic Learning**: Uses the Socratic method to guide students to answers
- **Hint-Based Assistance**: Provides progressive hints without spoiling the solution
- **Concept Explanation**: Breaks down complex topics into understandable chunks
- **Progress Tracking**: Monitors student learning patterns
- **Multiple Learning Strategies**: Adapts teaching approach based on question type

## Software Design Patterns Used

1. **Strategy Pattern**: Different teaching strategies (Socratic, Hints, Conceptual)
2. **Factory Pattern**: Creates appropriate response types based on context
3. **Observer Pattern**: Tracks and logs student progress
4. **Chain of Responsibility**: Routes questions to appropriate handlers
5. **Singleton Pattern**: Manages application configuration

## System Requirements

- **Processor**: Core i3 or better
- **RAM**: 4GB minimum (8GB recommended)
- **Storage**: 2GB for OLLAMA model
- **OS**: Windows/Linux/MacOS

## OLLAMA Setup

**Recommended Model for Core i3**: `phi3:mini` (3.8GB)
- Fast inference on limited hardware
- Good reasoning capabilities
- Alternative: `llama3.2:1b` (1.3GB) for even lighter setup

### Install OLLAMA:
1. Download from: https://ollama.ai/download
2. Install OLLAMA (Version 0.1.29 or later)
3. Run: `ollama pull phi3:mini`

## Installation

```bash
# Install Python dependencies
pip install -r requirements.txt

# Verify OLLAMA is running
ollama list
```

## Usage

```bash
# Run the chatbot
python main.py
```

## Project Structure

```
Study Assistant/
├── src/
│   ├── patterns/          # Design pattern implementations
│   ├── strategies/        # Learning strategies
│   ├── services/          # Core services
│   └── ui/               # User interface
├── config/               # Configuration files
├── data/                # Student progress data
└── tests/               # Unit tests
```

## Developer Notes

This is development code with:
- Extensive logging
- Modular architecture
- Easy extensibility
- Debug modes enabled

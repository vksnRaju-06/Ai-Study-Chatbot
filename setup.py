"""
Installation and Setup Script
Helps verify and configure the Study Assistant
"""

import subprocess
import sys
import os
from pathlib import Path


def print_header(text):
    """Print formatted header"""
    print("\n" + "=" * 60)
    print(text.center(60))
    print("=" * 60)


def check_python_version():
    """Check if Python version is adequate"""
    print_header("CHECKING PYTHON VERSION")
    version = sys.version_info
    print(f"Python {version.major}.{version.minor}.{version.micro}")
    
    if version.major >= 3 and version.minor >= 8:
        print("✅ Python version is adequate")
        return True
    else:
        print("❌ Python 3.8 or higher is required")
        return False


def install_requirements():
    """Install Python requirements"""
    print_header("INSTALLING PYTHON DEPENDENCIES")
    
    try:
        subprocess.check_call([
            sys.executable,
            "-m",
            "pip",
            "install",
            "-r",
            "requirements.txt",
            "--upgrade"
        ])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        return False


def check_ollama():
    """Check if OLLAMA is installed"""
    print_header("CHECKING OLLAMA")
    
    try:
        result = subprocess.run(
            ["ollama", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            print(f"✅ OLLAMA is installed: {result.stdout.strip()}")
            return True
        else:
            print("❌ OLLAMA not found")
            return False
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("❌ OLLAMA not found")
        return False


def check_ollama_model():
    """Check if the required model is downloaded"""
    print_header("CHECKING OLLAMA MODEL")
    
    try:
        result = subprocess.run(
            ["ollama", "list"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if "phi3:mini" in result.stdout or "phi3" in result.stdout:
            print("✅ phi3:mini model found")
            return True
        else:
            print("⚠️  phi3:mini model not found")
            print("\nTo install the model, run:")
            print("  ollama pull phi3:mini")
            return False
    except Exception as e:
        print(f"❌ Error checking model: {e}")
        return False


def create_env_file():
    """Create .env file from example"""
    print_header("CREATING CONFIGURATION")
    
    env_example = Path(".env.example")
    env_file = Path(".env")
    
    if env_file.exists():
        print("⚠️  .env file already exists")
        response = input("Overwrite? (y/n): ").lower()
        if response != 'y':
            print("Skipping .env creation")
            return True
    
    try:
        if env_example.exists():
            env_file.write_text(env_example.read_text())
            print("✅ Created .env file")
        else:
            # Create default .env
            default_env = """# OLLAMA Configuration
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=phi3:mini

# Application Settings
LOG_LEVEL=INFO
MAX_CONTEXT_LENGTH=2048
TEMPERATURE=0.7

# Database
DB_PATH=data/student_progress.db

# UI Settings
UI_THEME=light
"""
            env_file.write_text(default_env)
            print("✅ Created default .env file")
        return True
    except Exception as e:
        print(f"❌ Failed to create .env: {e}")
        return False


def create_directories():
    """Create necessary directories"""
    print_header("CREATING DIRECTORIES")
    
    dirs = ['data', 'logs']
    
    for dir_name in dirs:
        path = Path(dir_name)
        path.mkdir(exist_ok=True)
        print(f"✅ Created {dir_name}/ directory")
    
    return True


def print_ollama_instructions():
    """Print OLLAMA installation instructions"""
    print_header("OLLAMA INSTALLATION INSTRUCTIONS")
    
    print("""
To install OLLAMA:

1. Visit: https://ollama.ai/download

2. Download the installer for Windows

3. Run the installer

4. After installation, open a terminal and run:
   ollama pull phi3:mini

5. Verify by running:
   ollama list

Alternative lightweight model (for slower systems):
   ollama pull llama3.2:1b

For the Study Assistant, phi3:mini is recommended as it provides
good balance between performance and quality on Core i3 laptops.
""")


def run_tests():
    """Run basic tests"""
    print_header("RUNNING TESTS")
    
    print("Testing imports...")
    try:
        from src.patterns.singleton import ConfigManager
        from src.services.study_assistant import StudyAssistant
        print("✅ All imports successful")
        
        print("\nTesting configuration...")
        config = ConfigManager()
        print(f"  Model: {config.get('ollama.model')}")
        print(f"  Host: {config.get('ollama.host')}")
        print("✅ Configuration loaded")
        
        return True
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def main():
    """Main setup routine"""
    print_header("AI STUDY ASSISTANT - SETUP")
    print("This script will help you set up the Study Assistant")
    
    results = {}
    
    # Check Python
    results['python'] = check_python_version()
    
    # Create directories
    results['directories'] = create_directories()
    
    # Create .env
    results['config'] = create_env_file()
    
    # Install requirements
    if results['python']:
        results['requirements'] = install_requirements()
    else:
        results['requirements'] = False
    
    # Check OLLAMA
    results['ollama'] = check_ollama()
    
    if results['ollama']:
        results['model'] = check_ollama_model()
    else:
        results['model'] = False
        print_ollama_instructions()
    
    # Run tests
    if results['requirements']:
        results['tests'] = run_tests()
    else:
        results['tests'] = False
    
    # Summary
    print_header("SETUP SUMMARY")
    
    for check, passed in results.items():
        status = "✅" if passed else "❌"
        print(f"{status} {check.title()}")
    
    all_passed = all(results.values())
    
    if all_passed:
        print_header("SETUP COMPLETE!")
        print("""
Everything is ready! To start the Study Assistant:

  python main.py

Or for the demo:

  python demo.py

The web interface will open at http://localhost:8501
""")
    else:
        print_header("SETUP INCOMPLETE")
        print("""
Some checks failed. Please resolve the issues above and run setup again.

Most common issues:
- OLLAMA not installed: Visit https://ollama.ai/download
- Model not downloaded: Run 'ollama pull phi3:mini'
- Dependencies failed: Check your internet connection
""")


if __name__ == "__main__":
    main()

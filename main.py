"""
Main entry point for the Study Assistant application
"""

import sys
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.patterns.singleton import config

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.get('app.log_level', 'INFO')),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data/app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def main():
    """Main application entry point"""
    logger.info("Starting AI Study Assistant")
    
    # Create data directory if doesn't exist
    Path('data').mkdir(exist_ok=True)
    
    # Import and run Streamlit app
    import subprocess
    import sys
    
    streamlit_script = Path(__file__).parent / 'src' / 'ui' / 'streamlit_app.py'
    
    logger.info(f"Launching Streamlit UI: {streamlit_script}")
    
    subprocess.run([
        sys.executable,
        '-m',
        'streamlit',
        'run',
        str(streamlit_script),
        '--server.headless=true',
        '--browser.serverAddress=localhost',
        '--server.port=8501'
    ])


if __name__ == "__main__":
    main()

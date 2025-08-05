"""Main entry point for MCP Pokemon Server."""

import asyncio
import sys
from pathlib import Path

# Add src to Python path for imports
sys.path.insert(0, str(Path(__file__).parent))

from server.mcp_server import run_server
from config.logging import setup_logging, get_logger

# Setup logging first
setup_logging()
logger = get_logger(__name__)


def main():
    """Main entry point."""
    logger.info("Starting MCP Pokemon Server application")
    
    try:
        # Run the async server
        asyncio.run(run_server())
    except KeyboardInterrupt:
        logger.info("Application stopped by user")
    except Exception as e:
        logger.error("Application crashed", error=str(e), exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

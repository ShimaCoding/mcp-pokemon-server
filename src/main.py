"""Main entry point for MCP Pokemon Server."""

import sys
from pathlib import Path

# Add project root to Python path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(Path(__file__).parent))

from src.config.logging import get_logger, setup_logging
from src.server.mcp_server import run_server

# Setup logging first
setup_logging()
logger = get_logger(__name__)


def main():
    """Main entry point."""
    logger.info("Starting MCP Pokemon Server application")

    try:
        # Run the server directly (FastMCP handles asyncio internally)
        run_server()
    except KeyboardInterrupt:
        logger.info("Application stopped by user")
    except Exception as e:
        logger.error("Application crashed", error=str(e), exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

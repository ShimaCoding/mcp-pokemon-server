#!/usr/bin/env python3
"""Simple runner for MCP Pokemon Server"""

import sys
import os
from pathlib import Path

def main():
    # Get project paths
    project_root = Path(__file__).parent
    
    # Add project root to Python path
    sys.path.insert(0, str(project_root))
    
    # Set environment
    os.environ["PYTHONPATH"] = str(project_root)
    
    # Import and run the server directly
    from src.main import main as server_main
    
    try:
        server_main()
    except KeyboardInterrupt:
        print("🛑 Server stopped by user", file=sys.stderr)
    except Exception as e:
        print(f"❌ Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()

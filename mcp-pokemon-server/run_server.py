#!/usr/bin/env python3
"""Simple runner for MCP Pokemon Server"""

import subprocess
import sys
import os
from pathlib import Path

def main():
    # Get project paths
    project_root = Path(__file__).parent
    venv_python = "/Users/francobeltran/Code/Projects/mcp-test/.venv/bin/python"
    
    # Set environment
    env = os.environ.copy()
    env["PYTHONPATH"] = str(project_root)
    
    print("🎮 Starting MCP Pokemon Server...")
    print(f"📁 Project root: {project_root}")
    print(f"🐍 Python: {venv_python}")
    
    try:
        # Run the server
        cmd = [venv_python, "-m", "src.main"]
        subprocess.run(cmd, cwd=project_root, env=env, check=True)
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running server: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

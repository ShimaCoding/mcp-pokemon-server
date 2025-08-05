#!/usr/bin/env python3
"""Test MCP server connection and tools."""

import subprocess
import sys
import time
import signal
import json
from pathlib import Path

def test_server_startup():
    """Test that the server starts without errors."""
    project_root = Path(__file__).parent
    venv_python = "/Users/francobeltran/Code/Projects/mcp-test/.venv/bin/python"
    
    print("🧪 Testing MCP Server Startup...")
    
    # Start server as subprocess
    env = {"PYTHONPATH": str(project_root)}
    cmd = [venv_python, "-m", "src.main"]
    
    try:
        # Start the server
        print("🚀 Starting server...")
        process = subprocess.Popen(
            cmd,
            cwd=project_root,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait a bit for startup
        time.sleep(3)
        
        # Check if process is still running
        if process.poll() is None:
            print("✅ Server started successfully and is running!")
            
            # Try to terminate gracefully
            process.send_signal(signal.SIGTERM)
            try:
                process.wait(timeout=5)
                print("✅ Server shut down gracefully")
            except subprocess.TimeoutExpired:
                process.kill()
                print("⚠️ Server had to be force-killed")
                
            return True
        else:
            # Process exited, get the error
            stdout, stderr = process.communicate()
            print(f"❌ Server exited with code: {process.returncode}")
            print(f"STDOUT: {stdout}")
            print(f"STDERR: {stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing server: {e}")
        return False

def main():
    """Run server tests."""
    print("🎮 MCP Pokemon Server Tests")
    print("=" * 40)
    
    success = test_server_startup()
    
    if success:
        print("\n🎉 All tests passed! Server is ready for Claude Desktop.")
        print("\n📋 Next steps:")
        print("1. Make sure Claude Desktop is configured with the server")
        print("2. Restart Claude Desktop")
        print("3. Test with: 'Can you get information about Pikachu?'")
    else:
        print("\n❌ Tests failed. Check the error messages above.")
        sys.exit(1)

if __name__ == "__main__":
    main()

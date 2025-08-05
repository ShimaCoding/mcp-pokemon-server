#!/usr/bin/env python3
"""Test MCP server via stdio connection."""

import asyncio
import json
import subprocess
import sys
from pathlib import Path

class MCPStdioTester:
    def __init__(self):
        self.process = None
    
    async def start_server(self):
        """Start the MCP server process."""
        project_root = Path(__file__).parent
        venv_python = "/Users/francobeltran/Code/Projects/mcp-test/.venv/bin/python"
        
        env = {
            "PYTHONPATH": str(project_root)
        }
        
        cmd = [venv_python, "-m", "src.main"]
        
        print("🚀 Starting MCP server...")
        self.process = await asyncio.create_subprocess_exec(
            *cmd,
            cwd=project_root,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=env
        )
        print("✅ Server started!")
    
    async def send_request(self, request):
        """Send a JSON-RPC request to the server."""
        if not self.process:
            raise RuntimeError("Server not started")
        
        request_json = json.dumps(request) + "\n"
        print(f"📤 Sending: {request_json.strip()}")
        
        self.process.stdin.write(request_json.encode())
        await self.process.stdin.drain()
        
        # Read response
        response_line = await self.process.stdout.readline()
        response = json.loads(response_line.decode())
        print(f"📥 Received: {json.dumps(response, indent=2)}")
        return response
    
    async def test_initialize(self):
        """Test the initialize request."""
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {}
                },
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            }
        }
        return await self.send_request(request)
    
    async def test_list_tools(self):
        """Test the tools/list request."""
        request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list"
        }
        return await self.send_request(request)
    
    async def test_call_tool(self, tool_name, arguments):
        """Test calling a specific tool."""
        request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }
        return await self.send_request(request)
    
    async def cleanup(self):
        """Cleanup the server process."""
        if self.process:
            self.process.terminate()
            await self.process.wait()
            print("🛑 Server stopped")

async def main():
    """Run the stdio test."""
    tester = MCPStdioTester()
    
    try:
        # Start server
        await tester.start_server()
        await asyncio.sleep(1)  # Give server time to start
        
        # Test initialize
        print("\n=== Testing Initialize ===")
        init_response = await tester.test_initialize()
        
        # Test list tools
        print("\n=== Testing List Tools ===")
        tools_response = await tester.test_list_tools()
        
        # Test get_pokemon_info
        print("\n=== Testing get_pokemon_info ===")
        pokemon_response = await tester.test_call_tool(
            "get_pokemon_info", 
            {"name_or_id": "pikachu"}
        )
        
        print("\n🎉 All tests completed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await tester.cleanup()

if __name__ == "__main__":
    asyncio.run(main())

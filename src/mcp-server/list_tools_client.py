import asyncio
import os
from fastmcp import Client

async def main():
    """Connects to the local STDIO MCP server and lists all tools and their tags."""
    
    server_script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'server.py'))
    print(f"Connecting to STDIO server at: {server_script_path}\n")

    try:
        async with Client(server_script_path) as client:
            # The correct method to list tools is client.list_tools()
            all_tools = await client.list_tools()
            
            if not all_tools:
                print("No tools found on the server.")
                return

            print("--- All Available MCP Tools ---")
            for tool in all_tools:
                # Tags are stored in the meta attribute
                tags = tool.meta.get('_fastmcp', {}).get('tags', [])
                tag_str = f"(Tags: {', '.join(tags)})" if tags else "(No tags)"
                print(f"- {tool.name} {tag_str}")

    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(main())

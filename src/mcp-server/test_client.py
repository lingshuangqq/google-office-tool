import asyncio
import os
from fastmcp import Client

async def main():
    """Connects to the local STDIO MCP server and tests the 'doc' tools."""
    
    server_script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'server.py'))
    print(f"Connecting to STDIO server at: {server_script_path}")

    # The content for the initial document, including a placeholder
    initial_markdown = """
# Initial Document

This is the first version of the document.

My placeholder is: {{placeholder}}
"""

    # Content for the append operation
    append_markdown = """
## Appended Section

- This content was appended.
"""

    # Content to replace the placeholder
    replacement_markdown = "**REPLACED**"

    try:
        async with Client(server_script_path) as client:
            print("Successfully connected to server.")

            # --- 1. Create the initial document ---
            print("\n--- 1. Creating initial document ---")
            create_result = await client.call_tool(
                "create_google_doc_from_markdown",
                arguments={
                    "title": "MCP Full Test Document",
                    "markdown_content": initial_markdown,
                    "folder_id": "1rLrDv-BO_Pz-5UZTeJOKU56iNkLP2fJx",
                },
            )
            print("Create response:", create_result.data)
            document_id = create_result.data.get("document_id")

            if not document_id:
                print("\nTest failed: Could not create document.")
                return

            print(f"Document created with ID: {document_id}")
            # Give Google's API a moment to process
            await asyncio.sleep(2)

            # --- 2. Read the initial content ---
            print("\n--- 2. Reading initial content ---")
            read_result_1 = await client.call_tool(
                "read_google_doc_content", arguments={"document_id": document_id}
            )
            print("Read response 1:", read_result_1.data)
            await asyncio.sleep(2)

            # --- 3. Append content to the document ---
            print("\n--- 3. Appending content ---")
            append_result = await client.call_tool(
                "append_content_to_google_doc",
                arguments={
                    "document_id": document_id,
                    "markdown_content": append_markdown,
                },
            )
            print("Append response:", append_result.data)
            await asyncio.sleep(2)

            # --- 4. Replace the placeholder ---
            print("\n--- 4. Replacing placeholder ---")
            replace_result = await client.call_tool(
                "replace_placeholders_in_google_doc",
                arguments={
                    "document_id": document_id,
                    "placeholder": "{{placeholder}}",
                    "markdown_content": replacement_markdown,
                },
            )
            print("Replace response:", replace_result.data)
            await asyncio.sleep(2)

            # --- 5. Read the final content ---
            print("\n--- 5. Reading final content ---")
            read_result_2 = await client.call_tool(
                "read_google_doc_content", arguments={"document_id": document_id}
            )
            print("Read response 2:", read_result_2.data)
            await asyncio.sleep(2)

            # --- 6. Clear the document ---
            print("\n--- 6. Clearing the document ---")
            clear_result = await client.call_tool(
                "clear_google_doc_content", arguments={"document_id": document_id}
            )
            print("Clear response:", clear_result.data)
            await asyncio.sleep(2)

            # --- 7. Final read to confirm clearance ---
            print("\n--- 7. Final read to confirm clearance ---")
            read_result_3 = await client.call_tool(
                "read_google_doc_content", arguments={"document_id": document_id}
            )
            print("Read response 3:", read_result_3.data)

    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(main())

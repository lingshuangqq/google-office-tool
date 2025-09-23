import os
import sys
import tempfile
import json

from fastmcp import FastMCP

# Add the src directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from auth import get_services_with_oauth
from google_docs.write import write_to_google_doc
from google_docs.append import append_to_google_doc
from google_docs.clear import clear_google_doc
from google_docs.replace import replace_markdown_placeholders
from google_docs.read import read_google_doc
from google_slider.create import create_presentation_from_markdown

mcp = FastMCP("Google Office Tool 🚀")

# --- Helper function for authentication ---
def get_services():
    """Helper to get authenticated Google services using OAuth 2.0."""
    creds_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../credentials/oauth-credentials.json'))
    token_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../credentials/token.json'))
    
    if not os.path.exists(creds_path):
        raise FileNotFoundError(f"OAuth credentials file not found at {creds_path}")
        
    return get_services_with_oauth(creds_path, token_path)

# --- MCP Tools ---

@mcp.tool(tags=["doc"])
def create_google_doc_from_markdown(
    markdown_content: str,
    title: str,
    folder_id: str = None
) -> dict:
    """
    Creates a new Google Doc from markdown content.

    Args:
        markdown_content: The markdown content to write to the document.
        title: The title of the new document.
        folder_id: The ID of the Google Drive folder to create the document in.

    Returns:
        A dictionary containing the status and the document ID.
    """
    try:
        services = get_services()
        result = write_to_google_doc(
            docs_service=services["docs"],
            drive_service=services["drive"],
            markdown_content=markdown_content,
            title=title,
            folder_id=folder_id
        )
        return result
    except Exception as e:
        return {"status": "error", "message": str(e)}


@mcp.tool(tags=["doc"])
def append_content_to_google_doc(
    document_id: str,
    markdown_content: str
) -> dict:
    """
    Appends markdown content to an existing Google Doc.

    Args:
        document_id: The ID of the document to append to.
        markdown_content: The markdown content to append.

    Returns:
        A dictionary containing the status of the operation.
    """
    try:
        services = get_services()
        result = append_to_google_doc(
            docs_service=services["docs"],
            document_id=document_id,
            markdown_content=markdown_content
        )
        return result
    except Exception as e:
        return {"status": "error", "message": str(e)}


@mcp.tool(tags=["doc"])
def clear_google_doc_content(document_id: str) -> dict:
    """
    Clears all content from a Google Doc.

    Args:
        document_id: The ID of the document to clear.

    Returns:
        A dictionary containing the status of the operation.
    """
    try:
        services = get_services()
        result = clear_google_doc(
            docs_service=services["docs"],
            document_id=document_id
        )
        return result
    except Exception as e:
        return {"status": "error", "message": str(e)}


@mcp.tool(tags=["doc"])
def replace_placeholders_in_google_doc(
    document_id: str,
    placeholder: str,
    markdown_content: str
) -> dict:
    """
    Replaces a placeholder in a Google Doc with markdown content.

    Args:
        document_id: The ID of the document to modify.
        placeholder: The placeholder text to replace (e.g., '{{my_placeholder}}').
        markdown_content: The markdown content to insert.

    Returns:
        A dictionary containing the status of the operation.
    """
    try:
        services = get_services()
        replacements = {placeholder: markdown_content}
        result = replace_markdown_placeholders(
            docs_service=services["docs"],
            document_id=document_id,
            replacements=replacements
        )
        return result
    except Exception as e:
        return {"status": "error", "message": str(e)}


@mcp.tool(tags=["doc"])
def read_google_doc_content(document_id: str) -> dict:
    """
    Reads the text content of a Google Doc.

    Args:
        document_id: The ID of the document to read.

    Returns:
        A dictionary containing the status and the document content.
    """
    try:
        services = get_services()
        result = read_google_doc(
            docs_service=services["docs"],
            document_id=document_id
        )
        return result
    except Exception as e:
        return {"status": "error", "message": str(e)}


@mcp.tool(tags=["slider"])
def create_google_slides_presentation(
    markdown_content: str,
    title: str = None,
    folder_id: str = None,
    template_id: str = None
) -> dict:
    """
    Creates a new Google Slides presentation from markdown content.

    Args:
        markdown_content: The markdown content for the presentation.
        title: The title of the new presentation.
        folder_id: The ID of the Google Drive folder to create the presentation in.
        template_id: The ID of a Google Slides presentation to use as a template.

    Returns:
        A dictionary containing the status and the presentation ID.
    """
    try:
        services = get_services()
        # Create a temporary file to hold the markdown content
        with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.md') as temp_file:
            temp_file.write(markdown_content)
            temp_file_path = temp_file.name

        presentation = create_presentation_from_markdown(
            services=services,
            markdown_file=temp_file_path,
            drive_folder_id=folder_id,
            template_id=template_id,
            title=title
        )
        os.remove(temp_file_path)  # Clean up the temporary file

        if presentation:
            presentation_id = presentation.get('presentationId') or presentation.get('id')
            return {
                "status": "success",
                "message": f"Successfully created presentation: https://docs.google.com/presentation/d/{presentation_id}",
                "presentation_id": presentation_id
            }
        else:
            return {"status": "error", "message": "Failed to create presentation."}

    except Exception as e:
        # Clean up the temp file in case of an error
        if 'temp_file_path' in locals() and os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    mcp.run()
from .operations import create_doc, execute_batch_update
from .clear import clear_google_doc
from .append import append_to_google_doc

def write_to_google_doc(docs_service, drive_service, markdown_content: str, title: str = "Untitled Document", document_id: str = None, folder_id: str = None) -> dict:
    """Writes markdown content to a Google Doc, supporting all formats."""
    try:
        if not document_id:
            print("No document ID provided, creating a new document...")
            creation_result = create_doc(drive_service, title, folder_id)
            if creation_result["status"] == "error":
                return creation_result
            document_id = creation_result["document_id"]
            print(f"Successfully created new document with ID: {document_id}")
        
        print(f"Clearing document {document_id} before writing...")
        clear_result = clear_google_doc(docs_service, document_id)
        if clear_result["status"] == "error":
            # If clearing fails, it might be an empty doc, which is fine. Continue.
            print(f"Info: Could not clear document (might be empty). {clear_result['message']}")

        print("Appending content to the cleared document...")
        # Use the new, powerful append function to write the content.
        append_result = append_to_google_doc(docs_service, document_id, markdown_content)
        
        if append_result["status"] == "success":
            return {
                "status": "success",
                "message": f"Successfully wrote content to document {document_id}.",
                "document_id": document_id
            }
        else:
            # Prepend a message to clarify the context of the error.
            append_result["message"] = f"Failed to write content after clearing: {append_result['message']}"
            return append_result

    except Exception as e:
        return {"status": "error", "message": f"An unexpected error occurred during the write process: {e}"}
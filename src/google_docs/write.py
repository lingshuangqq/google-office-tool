from . import markdown_parser
from .operations import create_doc, execute_batch_update
from .clear import clear_google_doc

def write_to_google_doc(docs_service, drive_service, markdown_content: str, title: str = "Untitled Document", document_id: str = None, folder_id: str = None) -> dict:
    """
    Writes markdown content to a Google Doc. Creates a new doc if document_id is not provided.
    """
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
            print(f"Warning: Could not clear document. {clear_result['message']}")

        print("Converting markdown to Google Docs format...")
        requests = markdown_parser.get_markdown_requests(markdown_content, start_index=1)

        print("Writing content to the document...")
        write_result = execute_batch_update(docs_service, document_id, requests)
        
        if write_result["status"] == "success":
            return {
                "status": "success",
                "message": f"Successfully wrote content to document {document_id}.",
                "document_id": document_id
            }
        else:
            return write_result

    except Exception as e:
        return {"status": "error", "message": f"An unexpected error occurred during the write process: {e}"}

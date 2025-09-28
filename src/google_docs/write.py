from .operations import create_doc
from .clear import clear_google_doc
from .content_installer import install_content

def write_to_google_doc(docs_service, drive_service, markdown_content: str, title: str = "Untitled Document", document_id: str = None, folder_id: str = None) -> dict:
    """Writes content to a Google Doc by clearing it and then calling the content installer."""
    try:
        if not document_id:
            creation_result = create_doc(drive_service, title, folder_id)
            if creation_result["status"] == "error":
                return creation_result
            document_id = creation_result["document_id"]
        
        clear_result = clear_google_doc(docs_service, document_id)
        if clear_result["status"] == "error":
            print(f"Info: Could not clear document (might be empty). {clear_result['message']}")

        # Start the installation at the beginning of the document.
        install_result = install_content(docs_service, document_id, markdown_content, start_index=1)
        
        if install_result["status"] == "success":
            return {"status": "success", "document_id": document_id}
        else:
            return install_result

    except Exception as e:
        return {"status": "error", "message": f"An unexpected error occurred during the write process: {e}"}

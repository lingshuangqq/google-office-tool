from .content_installer import install_content, _get_end_index

def append_to_google_doc(docs_service, document_id: str, markdown_content: str) -> dict:
    """Appends content to the end of a Google Doc by calling the content installer."""
    try:
        # Find the end of the document and start the installation there.
        start_index = _get_end_index(docs_service, document_id)
        return install_content(docs_service, document_id, markdown_content, start_index)
    except Exception as e:
        return {"status": "error", "message": f"An error occurred in append: {e}"}
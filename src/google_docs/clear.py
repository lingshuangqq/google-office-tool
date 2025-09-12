from .operations import execute_batch_update

def clear_google_doc(docs_service, document_id: str) -> dict:
    """Deletes all content from a Google Doc."""
    try:
        doc = docs_service.documents().get(documentId=document_id).execute()
        body_content = doc.get('body', {}).get('content', [])
        if len(body_content) > 1:
            end_index = body_content[-1].get('endIndex', 1)
            if end_index > 2:
                requests = [{'deleteContentRange': {'range': {'startIndex': 1, 'endIndex': end_index - 1}}}]
                return execute_batch_update(docs_service, document_id, requests)
        return {"status": "success", "message": "Document is already empty."}
    except Exception as e:
        return {"status": "error", "message": f"An unexpected error occurred: {e}"}

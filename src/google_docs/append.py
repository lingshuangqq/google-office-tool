from . import markdown_parser
from .operations import execute_batch_update

def append_to_google_doc(docs_service, document_id: str, markdown_content: str) -> dict:
    """Appends formatted markdown content to the end of a Google Doc."""
    try:
        # First, get the current state of the document to find the end index
        doc = docs_service.documents().get(documentId=document_id).execute()
        body_content = doc.get('body', {}).get('content', [])
        
        # The end index of the last element is where we will start inserting.
        # We subtract 1 because the very end is a final newline character.
        # If the document is empty, we start at index 1.
        end_index = 1
        if len(body_content) > 1 and 'endIndex' in body_content[-1]:
            end_index = body_content[-1]['endIndex'] - 1

        # Ensure there is a newline before appending new content if the doc is not empty
        requests = []
        if end_index > 1:
            requests.append({
                'insertText': {
                    'location': {'index': end_index},
                    'text': '\n'
                }
            })
            end_index += 1 # Increment our start index to be after the newline

        # Get the requests for the new markdown content
        markdown_requests = markdown_parser.get_markdown_requests(markdown_content, end_index)
        requests.extend(markdown_requests)
        
        return execute_batch_update(docs_service, document_id, requests)

    except Exception as e:
        return {"status": "error", "message": f"An unexpected error occurred during the append process: {e}"}

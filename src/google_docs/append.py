import time
from . import markdown_parser
from .operations import execute_batch_update

def append_to_google_doc(docs_service, document_id: str, markdown_content: str) -> dict:
    """Appends mixed content to a Google Doc using an intelligent batching strategy."""
    
    operation_plan = markdown_parser.create_operation_plan(markdown_content)
    if not operation_plan:
        return {"status": "success", "message": "No content to append."}

    for operation in operation_plan:
        if operation['type'] == 'simple':
            result = _handle_simple_append(docs_service, document_id, operation['content'])
        elif operation['type'] == 'table':
            result = _handle_table_append(docs_service, document_id, operation['data'])
        else:
            result = {"status": "error", "message": f"Unknown operation type: {operation['type']}"}

        if result['status'] != 'success':
            return result

    return {"status": "success", "message": "Successfully appended all content blocks."}

def _get_end_index(docs_service, document_id: str) -> int:
    """Helper to find the last writable index in the document body."""
    try:
        doc = docs_service.documents().get(documentId=document_id, fields='body(content(endIndex))').execute()
        body_content = doc.get('body', {}).get('content', [])
        for element in reversed(body_content):
            if 'endIndex' in element:
                return element['endIndex'] - 1
        return 1
    except Exception:
        return 1

def _handle_table_append(docs_service, document_id: str, table_data: tuple):
    """Appends a table to the end of the document."""
    try:
        num_rows, num_cols, cell_contents = table_data
        requests_insert = [{'insertTable': {'rows': num_rows, 'columns': num_cols, 'endOfSegmentLocation': {'segmentId': ''}}}]
        
        insert_result = execute_batch_update(docs_service, document_id, requests_insert)
        if insert_result['status'] != 'success':
            return insert_result

        time.sleep(1)

        doc = docs_service.documents().get(documentId=document_id).execute()
        end_index = _get_end_index(docs_service, document_id)
        populate_requests = markdown_parser.find_table_and_get_cell_requests(doc.get('body', {}), num_rows, num_cols, cell_contents, end_index)
        
        if not populate_requests:
            return {"status": "error", "message": "Could not find table to populate cells."}

        return execute_batch_update(docs_service, document_id, populate_requests)

    except Exception as e:
        return {"status": "error", "message": f"An error occurred during table insertion: {e}"}

def _handle_simple_append(docs_service, document_id: str, markdown_content: str):
    """Appends a block of simple text to the end of the document."""
    try:
        end_index = _get_end_index(docs_service, document_id)
        requests = [{'insertText': {'location': {'index': end_index}, 'text': '\n'}}] # Corrected newline escape
        requests.extend(markdown_parser.get_simple_markdown_requests(markdown_content, end_index + 1)[0])

        result = execute_batch_update(docs_service, document_id, requests)
        if result['status'] == 'success':
            time.sleep(1)
        return result

    except Exception as e:
        return {"status": "error", "message": f"An error occurred during simple insertion: {e}"}
import time
from . import markdown_parser
from .operations import execute_batch_update

def append_to_google_doc(docs_service, document_id: str, markdown_content: str) -> dict:
    """Appends mixed content to a Google Doc using an intelligent batching strategy."""
    
    # 1. Create the operation plan from the markdown content.
    operation_plan = markdown_parser.create_operation_plan(markdown_content)
    if not operation_plan:
        return {"status": "success", "message": "No content to append."}

    # 2. Initialize the execution loop.
    pending_simple_requests = []
    current_index = _get_end_index(docs_service, document_id)

    # 3. Loop through the plan and execute.
    for operation in operation_plan:
        if operation['type'] == 'simple':
            # For simple text, generate requests and add them to the pending batch.
            # A newline is added to separate this block from the previous one.
            pending_simple_requests.append({'insertText': {'location': {'index': current_index}, 'text': '\n'}})
            current_index += 1
            
            requests, length = markdown_parser.get_simple_markdown_requests(operation['content'], current_index)
            pending_simple_requests.extend(requests)
            current_index += length

        elif operation['type'] == 'table':
            # If we encounter a table, first execute any pending simple requests.
            if pending_simple_requests:
                result = execute_batch_update(docs_service, document_id, pending_simple_requests)
                if result['status'] != 'success': return result
                pending_simple_requests = [] # Clear the batch
                time.sleep(1) # Pause after execution

            # Then, handle the table insertion.
            result = handle_table_insertion(docs_service, document_id, operation['data'])
            if result['status'] != 'success': return result
            
            # After a table is inserted, the index structure changes significantly.
            # We must refetch the end index for subsequent operations.
            current_index = _get_end_index(docs_service, document_id)

    # After the loop, execute any remaining simple requests.
    if pending_simple_requests:
        result = execute_batch_update(docs_service, document_id, pending_simple_requests)
        if result['status'] != 'success': return result

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

def handle_table_insertion(docs_service, document_id: str, table_data: tuple):
    """Executes the three-step process to insert and populate a table at the end of the document."""
    try:
        num_rows, num_cols, cell_contents = table_data
        requests_insert = [{'insertTable': {'rows': num_rows, 'columns': num_cols, 'endOfSegmentLocation': {'segmentId': ''}}}]
        
        insert_result = execute_batch_update(docs_service, document_id, requests_insert)
        if insert_result['status'] != 'success':
            return insert_result

        time.sleep(1)

        doc = docs_service.documents().get(documentId=document_id).execute()
        populate_requests = markdown_parser.find_table_and_get_cell_requests(doc.get('body', {}), num_rows, num_cols, cell_contents)
        
        if not populate_requests:
            return {"status": "error", "message": "Could not find table to populate cells."}

        return execute_batch_update(docs_service, document_id, populate_requests)

    except Exception as e:
        return {"status": "error", "message": f"An error occurred during table insertion: {e}"}

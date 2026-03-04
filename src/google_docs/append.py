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
        elif operation['type'] == 'list':
            result = _handle_list_append(docs_service, document_id, operation['lines'], operation['list_type'])
        elif operation['type'] == 'hr':
            result = _handle_hr_append(docs_service, document_id)
        elif operation['type'] == 'code_block':
            result = _handle_code_block_append(docs_service, document_id, operation['content'])
        elif operation['type'] == 'blockquote':
            result = _handle_blockquote_append(docs_service, document_id, operation['content'])
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

def _handle_list_append(docs_service, document_id: str, list_lines: list, list_type: str):
    """Appends a list to the end of the document."""
    try:
        end_index = _get_end_index(docs_service, document_id)
        requests = [{'insertText': {'location': {'index': end_index}, 'text': '\n'}}]
        
        list_requests, _ = markdown_parser.get_list_requests(list_lines, list_type, end_index + 1)
        requests.extend(list_requests)

        result = execute_batch_update(docs_service, document_id, requests)
        if result['status'] == 'success':
            time.sleep(1)
        return result

    except Exception as e:
        return {"status": "error", "message": f"An error occurred during list insertion: {e}"}

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

def _handle_hr_append(docs_service, document_id: str):
    """Appends a horizontal rule to the end of the document."""
    try:
        end_index = _get_end_index(docs_service, document_id)
        requests = [
            {'insertText': {'location': {'index': end_index}, 'text': '\n'}},
            {
                'updateParagraphStyle': {
                    'range': {'startIndex': end_index, 'endIndex': end_index + 1},
                    'paragraphStyle': {
                        'borderBottom': {
                            'color': {'color': {'rgbColor': {'red': 0, 'green': 0, 'blue': 0}}},
                            'width': {'magnitude': 1, 'unit': 'PT'},
                            'padding': {'magnitude': 0, 'unit': 'PT'},
                            'dashStyle': 'SOLID'
                        }
                    },
                    'fields': 'borderBottom'
                }
            },
            {'insertText': {'location': {'index': end_index + 1}, 'text': '\n'}}
        ]
        
        result = execute_batch_update(docs_service, document_id, requests)
        if result['status'] == 'success':
            time.sleep(1)
        return result

    except Exception as e:
        return {"status": "error", "message": f"An error occurred during HR insertion: {e}"}

def _handle_code_block_append(docs_service, document_id: str, code_content: str):
    """Appends a code block to the end of the document."""
    try:
        end_index = _get_end_index(docs_service, document_id)
        # Add leading newline to match append behavior
        requests = [{'insertText': {'location': {'index': end_index}, 'text': '\n'}}]
        code_requests, _ = markdown_parser.get_code_block_requests(code_content, end_index + 1)
        requests.extend(code_requests)
        
        result = execute_batch_update(docs_service, document_id, requests)
        if result['status'] == 'success':
            time.sleep(1)
        return result

    except Exception as e:
        return {"status": "error", "message": f"An error occurred during code block insertion: {e}"}

def _handle_blockquote_append(docs_service, document_id: str, blockquote_content: str):
    """Appends a blockquote to the end of the document."""
    try:
        end_index = _get_end_index(docs_service, document_id)
        # Add leading newline to match append behavior
        requests = [{'insertText': {'location': {'index': end_index}, 'text': '\n'}}]
        quote_requests, _ = markdown_parser.get_blockquote_requests(blockquote_content, end_index + 1)
        requests.extend(quote_requests)
        
        result = execute_batch_update(docs_service, document_id, requests)
        if result['status'] == 'success':
            time.sleep(1)
        return result

    except Exception as e:
        return {"status": "error", "message": f"An error occurred during blockquote insertion: {e}"}


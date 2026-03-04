# src/google_docs/content_installer.py

import time
from . import markdown_parser
from .operations import execute_batch_update

def install_content(docs_service, document_id: str, markdown_content: str, start_index: int):
    """Processes and installs mixed content at a specific index in a document."""
    
    operation_plan = markdown_parser.create_operation_plan(markdown_content)
    if not operation_plan:
        return {"status": "success", "message": "No content to install."}

    current_index = start_index

    for operation in operation_plan:
        if operation['type'] == 'simple':
            result = _handle_simple_insertion_at_index(docs_service, document_id, operation['content'], current_index)
            if result['status'] != 'success': return result
            current_index = _get_end_index(docs_service, document_id)

        elif operation['type'] == 'table':
            result = _handle_table_insertion_at_index(docs_service, document_id, operation['data'], current_index)
            if result['status'] != 'success': return result
            current_index = _get_end_index(docs_service, document_id)

        elif operation['type'] == 'list':
            result = _handle_list_insertion_at_index(docs_service, document_id, operation['lines'], operation['list_type'], current_index)
            if result['status'] != 'success': return result
            current_index = _get_end_index(docs_service, document_id)

        elif operation['type'] == 'hr':
            result = _handle_hr_insertion_at_index(docs_service, document_id, current_index)
            if result['status'] != 'success': return result
            current_index = _get_end_index(docs_service, document_id)

        elif operation['type'] == 'code_block':
            result = _handle_code_block_insertion_at_index(docs_service, document_id, operation['content'], current_index)
            if result['status'] != 'success': return result
            current_index = _get_end_index(docs_service, document_id)

    return {"status": "success", "message": "Successfully installed all content blocks."}

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

def _handle_table_insertion_at_index(docs_service, document_id: str, table_data: tuple, start_index: int):
    """Executes the three-step process for a single table at a specific index."""
    try:
        num_rows, num_cols, cell_contents = table_data
        # Add leading newline to match append behavior
        requests_insert = [
            {'insertText': {'location': {'index': start_index}, 'text': '\n'}},
            {'insertTable': {'rows': num_rows, 'columns': num_cols, 'location': {'index': start_index + 1}}}
        ]
        
        insert_result = execute_batch_update(docs_service, document_id, requests_insert)
        if insert_result['status'] != 'success':
            return insert_result

        time.sleep(1)

        doc = docs_service.documents().get(documentId=document_id).execute()
        populate_requests = markdown_parser.find_table_and_get_cell_requests(doc.get('body', {}), num_rows, num_cols, cell_contents, start_index + 1)
        
        if not populate_requests:
            return {"status": "error", "message": "Could not find table to populate cells."}

        return execute_batch_update(docs_service, document_id, populate_requests)

    except Exception as e:
        return {"status": "error", "message": f"An error occurred during table insertion: {e}"}

def _handle_simple_insertion_at_index(docs_service, document_id: str, markdown_content: str, start_index: int):
    try:
        # Add leading newline to match append behavior
        requests = [{'insertText': {'location': {'index': start_index}, 'text': '\n'}}]
        simple_requests, _ = markdown_parser.get_simple_markdown_requests(markdown_content, start_index + 1)
        requests.extend(simple_requests)
        
        if not simple_requests:
             return {"status": "success", "message": "No content to append."}

        result = execute_batch_update(docs_service, document_id, requests)
        if result['status'] == 'success':
            time.sleep(1)
        return result

    except Exception as e:
        return {"status": "error", "message": f"An error occurred during simple insertion: {e}"}

def _handle_list_insertion_at_index(docs_service, document_id: str, list_lines: list, list_type: str, start_index: int):
    try:
        # Add leading newline to match append behavior
        requests = [{'insertText': {'location': {'index': start_index}, 'text': '\n'}}]
        list_requests, _ = markdown_parser.get_list_requests(list_lines, list_type, start_index + 1)
        requests.extend(list_requests)
        
        if not list_requests:
             return {"status": "success", "message": "No list content to append."}

        result = execute_batch_update(docs_service, document_id, requests)
        if result['status'] == 'success':
            time.sleep(1)
        return result

    except Exception as e:
        return {"status": "error", "message": f"An error occurred during list insertion: {e}"}

def _handle_hr_insertion_at_index(docs_service, document_id: str, start_index: int):
    try:
        requests = [
            {'insertText': {'location': {'index': start_index}, 'text': '\n'}},
            {
                'updateParagraphStyle': {
                    'range': {'startIndex': start_index, 'endIndex': start_index + 1},
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
            {'insertText': {'location': {'index': start_index + 1}, 'text': '\n'}}
        ]
        
        result = execute_batch_update(docs_service, document_id, requests)
        if result['status'] == 'success':
            time.sleep(1)
        return result

    except Exception as e:
        return {"status": "error", "message": f"An error occurred during HR insertion: {e}"}

def _handle_code_block_insertion_at_index(docs_service, document_id: str, code_content: str, start_index: int):
    try:
        # Add leading newline to match append behavior
        requests = [{'insertText': {'location': {'index': start_index}, 'text': '\n'}}]
        code_requests, _ = markdown_parser.get_code_block_requests(code_content, start_index + 1)
        requests.extend(code_requests)
        
        result = execute_batch_update(docs_service, document_id, requests)
        if result['status'] == 'success':
            time.sleep(1)
        return result

    except Exception as e:
        return {"status": "error", "message": f"An error occurred during code block insertion: {e}"}


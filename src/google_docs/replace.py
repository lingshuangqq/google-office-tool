from .operations import execute_batch_update
from .content_installer import install_content
import re

def replace_markdown_placeholders(docs_service, document_id: str, replacements: dict):
    """Finds and replaces a placeholder with complex content by calling the content installer."""
    try:
        if not replacements:
            return {"status": "success", "message": "No replacements specified."}

        # For simplicity, this refactored version handles one placeholder at a time.
        key_to_replace, markdown_content = next(iter(replacements.items()))

        # Step 1: Find the placeholder's location.
        doc = docs_service.documents().get(documentId=document_id, fields='body(content)').execute()
        content = doc.get('body', {}).get('content', [])
        
        found_range = None
        for element in content:
            if 'paragraph' in element:
                for run in element['paragraph']['elements']:
                    if 'textRun' in run and run['textRun']['content']:
                        if key_to_replace in run['textRun']['content']:
                            for match in re.finditer(re.escape(key_to_replace), run['textRun']['content']):
                                start = run['startIndex'] + match.start()
                                end = run['startIndex'] + match.end()
                                found_range = {'startIndex': start, 'endIndex': end}
                                break
                    if found_range: break
            if found_range: break

        if not found_range:
            return {"status": "error", "message": f"Placeholder '{key_to_replace}' not found."}

        # Step 2: Delete the placeholder.
        delete_request = [{'deleteContentRange': {'range': found_range}}]
        delete_result = execute_batch_update(docs_service, document_id, delete_request)
        if delete_result['status'] != 'success':
            return delete_result

        # Step 3: Install the new content at the placeholder's original start index.
        return install_content(docs_service, document_id, markdown_content, found_range['startIndex'])

    except Exception as e:
        return {"status": "error", "message": f"An unexpected error occurred during replace: {e}"}

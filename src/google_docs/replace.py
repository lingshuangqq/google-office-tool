from .operations import execute_batch_update
import re

def replace_markdown_placeholders(docs_service, document_id: str, replacements: dict):
    """Finds a placeholder and replaces it with simple text for verification."""
    try:
        doc = docs_service.documents().get(documentId=document_id, fields='body(content)').execute()
        content = doc.get('body', {}).get('content', [])
        
        found_holders = []
        for key in replacements.keys():
            for element in content:
                if 'paragraph' in element:
                    for run in element['paragraph']['elements']:
                        if 'textRun' in run and run['textRun']['content']:
                            if key in run['textRun']['content']:
                                # Found a potential match. Now, get its precise range.
                                for match in re.finditer(re.escape(key), run['textRun']['content']):
                                    start = run['startIndex'] + match.start()
                                    end = run['startIndex'] + match.end()
                                    found_holders.append({'key': key, 'range': {'startIndex': start, 'endIndex': end}})

        if not found_holders:
            return {"status": "error", "message": "Placeholder not found."}

        # For this test, just use the first one found.
        holder = found_holders[0]
        
        requests = [
            {'deleteContentRange': {'range': holder['range']}},
            {'insertText': {
                'location': {'index': holder['range']['startIndex']},
                'text': '---> PLACEHOLDER REPLACED SUCCESSFULLY <---'
            }}
        ]
        
        return execute_batch_update(docs_service, document_id, requests)

    except Exception as e:
        return {"status": "error", "message": f"An unexpected error occurred during replace: {e}"}
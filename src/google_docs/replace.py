import re
from . import markdown_parser
from .operations import execute_batch_update

def replace_markdown_placeholders(docs_service, document_id: str, replacements: dict):
    """Finds and replaces multiple placeholders with formatted markdown content."""
    try:
        doc = docs_service.documents().get(documentId=document_id, fields='body(content)').execute()
        content = doc.get('body', {}).get('content', [])
        
        found_holders = []
        for element in content:
            if 'paragraph' in element:
                for run in element['paragraph']['elements']:
                    if 'textRun' in run and run['textRun']['content']:
                        segment_text = run['textRun']['content']
                        for key in replacements.keys():
                            for match in re.finditer(re.escape('{{' + key + '}}'), segment_text):
                                start = run['startIndex'] + match.start()
                                end = run['startIndex'] + match.end()
                                found_holders.append({'key': key, 'range': {'startIndex': start, 'endIndex': end}})

        found_holders.sort(key=lambda x: x['range']['startIndex'], reverse=True)
        
        if not found_holders:
            return {"status": "error", "message": "Could not find any of the specified placeholders."}

        all_requests = []
        for holder in found_holders:
            key = holder['key']
            markdown_content = replacements[key]
            start_index = holder['range']['startIndex']

            all_requests.append({'deleteContentRange': {'range': holder['range']}})
            markdown_requests = markdown_parser.get_markdown_requests(markdown_content, start_index)
            all_requests.extend(markdown_requests)
            
        return execute_batch_update(docs_service, document_id, all_requests)

    except Exception as e:
        return {"status": "error", "message": f"An unexpected error occurred: {e}"}

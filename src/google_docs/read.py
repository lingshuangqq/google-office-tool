def read_google_doc(docs_service, document_id: str):
    """Reads a Google Doc and returns its text content."""
    try:
        doc = docs_service.documents().get(documentId=document_id).execute()
        content = doc.get('body', {}).get('content', [])
        
        doc_content = ""
        for element in content:
            if 'paragraph' in element:
                elements = element.get('paragraph').get('elements')
                for elem in elements:
                    text_run = elem.get('textRun')
                    if text_run:
                        doc_content += text_run.get('content')
        return {"status": "success", "content": doc_content}
    except Exception as e:
        return {"status": "error", "message": f"An error occurred reading the document: {e}"}

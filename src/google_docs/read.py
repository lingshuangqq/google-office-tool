def read_google_doc(docs_service, document_id: str):
    """Reads a Google Doc and returns its text content."""
    try:
        doc = docs_service.documents().get(documentId=document_id).execute()
        content = doc.get('body', {}).get('content', [])
        
        doc_content = read_structural_elements(content)
        return {"status": "success", "content": doc_content}
    except Exception as e:
        return {"status": "error", "message": f"An error occurred reading the document: {e}"}

def read_structural_elements(elements):
    """Recursively reads structural elements from a Google Doc."""
    text = ""
    for value in elements:
        if 'paragraph' in value:
            elements = value.get('paragraph').get('elements')
            for elem in elements:
                text_run = elem.get('textRun')
                if text_run:
                    text += text_run.get('content')
        elif 'table' in value:
            table = value.get('table')
            for row in table.get('tableRows', []):
                row_text = []
                for cell in row.get('tableCells', []):
                    cell_content = read_structural_elements(cell.get('content', []))
                    # Strip trailing newlines from cell content for cleaner table formatting
                    row_text.append(cell_content.strip())
                
                # Format as a simple markdown-like table row
                if row_text:
                    text += "| " + " | ".join(row_text) + " |\n"
            text += "\n"  # Add spacing after the table
    return text

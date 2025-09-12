from googleapiclient.errors import HttpError

def execute_batch_update(docs_service, document_id: str, requests: list) -> dict:
    """Executes a batchUpdate request and handles common errors."""
    try:
        if not requests:
            return {"status": "success", "message": "No changes were needed."}
        docs_service.documents().batchUpdate(documentId=document_id, body={'requests': requests}).execute()
        return {"status": "success", "message": f"Successfully updated document {document_id}."}
    except HttpError as err:
        return {"status": "error", "message": f"An HttpError occurred: {err.reason}"}
    except Exception as e:
        return {"status": "error", "message": f"An unexpected error occurred: {e}"}

def create_doc(drive_service, title: str, folder_id: str = None):
    """Creates a new Google Doc."""
    file_metadata = {'name': title, 'mimeType': 'application/vnd.google-apps.document'}
    if folder_id:
        file_metadata['parents'] = [folder_id]
    try:
        file = drive_service.files().create(body=file_metadata, fields='id').execute()
        return {"status": "success", "document_id": file.get('id')}
    except Exception as e:
        return {"status": "error", "message": f"An error occurred creating the document: {e}"}

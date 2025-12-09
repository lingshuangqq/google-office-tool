import json
import os
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

def execute_batch_update(docs_service, document_id: str, requests: list) -> dict:
    """Executes a batchUpdate request and returns the API response."""
    try:
        if not requests:
            return {"status": "success", "message": "No changes were needed."}
        
        response = docs_service.documents().batchUpdate(documentId=document_id, body={'requests': requests}).execute()
        return {"status": "success", "message": f"Successfully updated document {document_id}.", "api_response": response}
    except HttpError as err:
        # Extracting the error message from the HttpError
        error_details = str(err)
        try:
            error_json = json.loads(err.content.decode('utf-8'))
            error_message = error_json.get('error', {}).get('message', error_details)
        except (json.JSONDecodeError, AttributeError):
            error_message = error_details
        return {"status": "error", "message": f"An HttpError occurred: {error_message}"}
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

def upload_public_image(drive_service, file_path: str) -> str:
    """Uploads an image to Drive, makes it public, and returns the webContentLink."""
    try:
        # Guess mimetype based on extension or default to jpeg
        _, ext = os.path.splitext(file_path)
        mime_type = 'image/png' if ext.lower() == '.png' else 'image/jpeg'
        
        media = MediaFileUpload(file_path, mimetype=mime_type)
        file_metadata = {'name': f'header_image_{os.path.basename(file_path)}'}
        
        file = drive_service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, webContentLink'
        ).execute()
        file_id = file.get('id')
        
        drive_service.permissions().create(
            fileId=file_id,
            body={'role': 'reader', 'type': 'anyone'}
        ).execute()
        
        return file.get('webContentLink')
    except Exception as e:
        raise Exception(f"Failed to upload image: {e}")

def add_header_with_image(docs_service, document_id: str, image_url: str):
    """Creates a header and inserts an image into it."""
    try:
        # Create Header
        req_create = [{'createHeader': {'type': 'DEFAULT'}}]
        res = docs_service.documents().batchUpdate(documentId=document_id, body={'requests': req_create}).execute()
        header_id = res['replies'][0]['createHeader']['headerId']
        
        # Insert Image
        req_insert = [{
            'insertInlineImage': {
                'uri': image_url,
                'location': {
                    'segmentId': header_id,
                    'index': 0
                }
            }
        }]
        return execute_batch_update(docs_service, document_id, req_insert)
    except Exception as e:
        return {"status": "error", "message": f"Failed to add header image: {e}"}
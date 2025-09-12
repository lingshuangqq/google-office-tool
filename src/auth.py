import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials as ServiceAccountCredentials

# Define the scope of permissions we are requesting
SCOPES = ["https://www.googleapis.com/auth/documents", "https://www.googleapis.com/auth/presentations", "https://www.googleapis.com/auth/drive.file"]

def get_services_with_oauth(client_secrets_path: str, token_path: str = "token.json"):
    """Handles the OAuth 2.0 flow and returns authorized service objects for Docs, Slides and Drive."""
    creds = None
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(client_secrets_path, SCOPES)
            creds = flow.run_local_server(port=0)
        
        with open(token_path, 'w') as token:
            token.write(creds.to_json())
            print(f"OAuth token has been saved to {token_path} for future use.")
            
    docs_service = build("docs", "v1", credentials=creds)
    slides_service = build("slides", "v1", credentials=creds)
    drive_service = build("drive", "v3", credentials=creds)
    return {"docs": docs_service, "slides": slides_service, "drive": drive_service}

def get_services_with_service_account(sa_file_path: str):
    """Handles Service Account authentication and returns authorized service objects for Docs, Slides and Drive."""
    creds = ServiceAccountCredentials.from_service_account_file(sa_file_path, scopes=SCOPES)
    docs_service = build("docs", "v1", credentials=creds)
    slides_service = build("slides", "v1", credentials=creds)
    drive_service = build("drive", "v3", credentials=creds)
    return {"docs": docs_service, "slides": slides_service, "drive": drive_service}

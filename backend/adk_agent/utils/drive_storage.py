# Copyright (c) 2025 Deepak Kushwah. All rights reserved.
import os.path
from typing import Optional
import streamlit as st
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/drive.file"]

class DriveManager:
    def __init__(self):
        self.creds = None
        self.service = None
        self.authenticate()

    def authenticate(self):
        """Authenticates the user using OAuth 2.0."""
        if os.path.exists("token.json"):
            self.creds = Credentials.from_authorized_user_file("token.json", SCOPES)
        
        # If there are no (valid) credentials available, let the user log in.
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                try:
                    self.creds.refresh(Request())
                except Exception:
                    self.creds = None # Force re-login if refresh fails
            
            if not self.creds:
                if not os.path.exists("client_secrets.json"):
                    st.error("Missing 'client_secrets.json'. Please add it to the root directory.")
                    return

                try:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        "client_secrets.json", SCOPES
                    )
                    # Run local server for auth
                    # Note: This requires the app to be running locally on a machine with a browser.
                    self.creds = flow.run_local_server(port=0)
                    
                    # Save the credentials for the next run
                    with open("token.json", "w") as token:
                        token.write(self.creds.to_json())
                except Exception as e:
                    st.error(f"Authentication Failed: {e}")
                    return

        try:
            self.service = build("drive", "v3", credentials=self.creds)
        except Exception as e:
            st.error(f"Failed to build Drive Service: {e}")

    def upload_file(self, file_obj, filename: str, folder_name: str = "PolicyPARAKH_Data") -> Optional[str]:
        """
        Uploads a file-like object to a specific folder in Google Drive.
        Returns the File ID or None.
        """
        if not self.service:
            return None

        try:
            # 1. Find or Create Folder
            folder_id = self._get_folder_id(folder_name)
            if not folder_id:
                folder_id = self._create_folder(folder_name)

            # 2. Upload File
            file_metadata = {
                "name": filename,
                "parents": [folder_id]
            }
            
            media = MediaIoBaseUpload(file_obj, mimetype="application/pdf", resumable=True)
            
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields="id"
            ).execute()
            
            return file.get("id")

        except Exception as e:
            st.error(f"Upload Failed: {e}")
            return None

    def _get_folder_id(self, folder_name: str):
        """Searches for a folder by name."""
        try:
            query = f"mimeType='application/vnd.google-apps.folder' and name='{folder_name}' and trashed=false"
            results = self.service.files().list(q=query, spaces='drive', fields='files(id, name)').execute()
            items = results.get('files', [])
            if not items:
                return None
            return items[0]['id']
        except:
            return None

    def _create_folder(self, folder_name: str):
        """Creates a new folder."""
        try:
            file_metadata = {
                "name": folder_name,
                "mimeType": "application/vnd.google-apps.folder"
            }
            file = self.service.files().create(body=file_metadata, fields="id").execute()
            return file.get("id")
        except:
            return None

    def find_file(self, filename: str, folder_name: str = "PolicyPARAKH_Data") -> Optional[str]:
        """Finds a file by name in the specific folder."""
        if not self.service: return None
        
        folder_id = self._get_folder_id(folder_name)
        if not folder_id: return None
        
        try:
            query = f"name='{filename}' and '{folder_id}' in parents and trashed=false"
            results = self.service.files().list(q=query, spaces='drive', fields='files(id, name)').execute()
            items = results.get('files', [])
            if not items: return None
            return items[0]['id']
        except:
            return None

    def download_file(self, file_id: str) -> Optional[str]:
        """Downloads a file content as string."""
        if not self.service: return None
        try:
            from googleapiclient.http import MediaIoBaseDownload
            import io
            
            request = self.service.files().get_media(fileId=file_id)
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while done is False:
                status, done = downloader.next_chunk()
            
            return fh.getvalue().decode('utf-8')
        except Exception as e:
            st.error(f"Download Failed: {e}")
            return None
            
    def update_file(self, file_id: str, content: str):
        """Updates an existing file content."""
        if not self.service: return None
        try:
            from googleapiclient.http import MediaIoBaseUpload
            import io
            
            media = MediaIoBaseUpload(io.BytesIO(content.encode('utf-8')), mimetype="application/json", resumable=True)
            self.service.files().update(fileId=file_id, media_body=media).execute()
            return True
        except Exception as e:
            st.error(f"Update Failed: {e}")
            return False

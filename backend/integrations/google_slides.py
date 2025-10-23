"""
Google Slides API integration for fetching presentation content.
"""
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from typing import List, Dict, Any, Optional
from config import settings


class GoogleSlidesClient:
    """Client for interacting with Google Slides API."""
    
    SCOPES = [
        'https://www.googleapis.com/auth/presentations.readonly',
        'https://www.googleapis.com/auth/drive.readonly'
    ]
    
    def __init__(self, credentials_path: Optional[str] = None):
        self.credentials_path = credentials_path or settings.google_application_credentials
        self.slides_service = None
        self.drive_service = None
        self._initialize_services()
    
    def _initialize_services(self):
        """Initialize Google API services with credentials."""
        if not self.credentials_path:
            return
        
        try:
            credentials = service_account.Credentials.from_service_account_file(
                self.credentials_path,
                scopes=self.SCOPES
            )
            
            self.slides_service = build('slides', 'v1', credentials=credentials)
            self.drive_service = build('drive', 'v3', credentials=credentials)
        except Exception as e:
            print(f"Warning: Failed to initialize Google services: {e}")
    
    def get_presentation(self, presentation_id: str) -> Dict[str, Any]:
        """
        Fetch a presentation's content.
        
        Args:
            presentation_id: The presentation ID
            
        Returns:
            Presentation data
        """
        if not self.slides_service:
            raise ValueError("Google Slides service not initialized")
        
        try:
            presentation = self.slides_service.presentations().get(
                presentationId=presentation_id
            ).execute()
            return presentation
        except HttpError as e:
            print(f"Error fetching presentation {presentation_id}: {e}")
            return {}
    
    def list_all_folders_recursive(self, folder_id: str) -> List[str]:
        """
        Recursively get all folder IDs under a parent folder.
        
        Args:
            folder_id: The parent folder ID
            
        Returns:
            List of all folder IDs (including parent)
        """
        if not self.drive_service:
            return []
        
        all_folders = [folder_id]
        
        try:
            # Get all folders in this folder
            query = f"'{folder_id}' in parents and mimeType='application/vnd.google-apps.folder'"
            results = self.drive_service.files().list(
                q=query,
                fields="files(id, name)"
            ).execute()
            
            subfolders = results.get('files', [])
            
            # Recursively get subfolders
            for subfolder in subfolders:
                subfolder_id = subfolder['id']
                all_folders.extend(self.list_all_folders_recursive(subfolder_id))
            
            return all_folders
        except HttpError as e:
            print(f"Error listing folders: {e}")
            return all_folders
    
    def list_presentations_in_folder(self, folder_id: Optional[str] = None, recursive: bool = True) -> List[Dict[str, Any]]:
        """
        List all presentations in a Google Drive folder and optionally all subfolders.
        
        Args:
            folder_id: The Drive folder ID (uses config if not provided)
            recursive: If True, includes all subfolders (default: True)
            
        Returns:
            List of presentation metadata
        """
        folder_id = folder_id or settings.google_drive_folder_id
        if not folder_id or not self.drive_service:
            return []
        
        all_presentations = []
        
        try:
            # Get all folder IDs to search
            if recursive:
                folder_ids = self.list_all_folders_recursive(folder_id)
                print(f"Searching {len(folder_ids)} folders (root + subfolders)...")
            else:
                folder_ids = [folder_id]
            
            # Search for presentations in all folders
            for fid in folder_ids:
                query = f"'{fid}' in parents and mimeType='application/vnd.google-apps.presentation'"
                results = self.drive_service.files().list(
                    q=query,
                    fields="files(id, name, modifiedTime, webViewLink)",
                    orderBy="modifiedTime desc"
                ).execute()
                
                presentations = results.get('files', [])
                all_presentations.extend(presentations)
            
            print(f"Found {len(all_presentations)} total presentations")
            return all_presentations
            
        except HttpError as e:
            print(f"Error listing presentations: {e}")
            return []
    
    def extract_text_from_presentation(self, presentation_id: str) -> Dict[str, Any]:
        """
        Extract all text content from a presentation.
        
        Args:
            presentation_id: The presentation ID
            
        Returns:
            Structured text content
        """
        presentation = self.get_presentation(presentation_id)
        if not presentation:
            return {}
        
        slides_content = []
        
        for i, slide in enumerate(presentation.get('slides', []), 1):
            slide_data = {
                "slide_number": i,
                "object_id": slide.get('objectId', ''),
                "texts": [],
                "speaker_notes": ""
            }
            
            # Extract text from page elements
            for element in slide.get('pageElements', []):
                if 'shape' in element:
                    shape = element['shape']
                    if 'text' in shape:
                        text_content = self._extract_text_from_element(shape['text'])
                        if text_content:
                            slide_data["texts"].append(text_content)
                
                elif 'table' in element:
                    table = element['table']
                    for row in table.get('tableRows', []):
                        for cell in row.get('tableCells', []):
                            if 'text' in cell:
                                text_content = self._extract_text_from_element(cell['text'])
                                if text_content:
                                    slide_data["texts"].append(text_content)
            
            # Extract speaker notes
            notes = slide.get('slideProperties', {}).get('notesPage', {})
            for element in notes.get('pageElements', []):
                if 'shape' in element:
                    shape = element['shape']
                    if 'text' in shape:
                        notes_text = self._extract_text_from_element(shape['text'])
                        if notes_text:
                            slide_data["speaker_notes"] += notes_text + " "
            
            slides_content.append(slide_data)
        
        return {
            "presentation_id": presentation_id,
            "title": presentation.get('title', ''),
            "slides": slides_content
        }
    
    def _extract_text_from_element(self, text_element: Dict[str, Any]) -> str:
        """
        Extract text from a text element.
        
        Args:
            text_element: Text element dictionary
            
        Returns:
            Concatenated text content
        """
        text_parts = []
        for run in text_element.get('textElements', []):
            if 'textRun' in run:
                content = run['textRun'].get('content', '')
                text_parts.append(content)
        
        return ''.join(text_parts).strip()
    
    def get_all_presentations_content(self, folder_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get content from all presentations in a folder.
        
        Args:
            folder_id: The Drive folder ID
            
        Returns:
            List of presentation contents
        """
        presentations = self.list_presentations_in_folder(folder_id)
        all_content = []
        
        for pres in presentations:
            content = self.extract_text_from_presentation(pres['id'])
            content['name'] = pres['name']
            content['modified_time'] = pres.get('modifiedTime', '')
            content['web_view_link'] = pres.get('webViewLink', '')
            all_content.append(content)
        
        return all_content


# Global Google Slides client instance
google_slides_client = GoogleSlidesClient()


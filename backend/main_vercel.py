from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import requests
from typing import Optional, Dict, Any
import json

app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatMessage(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str
    export_data: Optional[Dict[str, Any]] = None

# Initialize Figma client
class FigmaClient:
    def __init__(self):
        self.access_token = os.getenv("FIGMA_ACCESS_TOKEN")
        self.team_id = os.getenv("FIGMA_TEAM_ID")
        self.base_url = "https://api.figma.com/v1"
        self.headers = {"X-Figma-Token": self.access_token}
    
    def search_team_files(self, query: str) -> list:
        """Search for files in the team"""
        try:
            url = f"{self.base_url}/teams/{self.team_id}/projects"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            projects = response.json().get("projects", [])
            files = []
            
            for project in projects:
                project_id = project.get("id")
                if project_id:
                    files_url = f"{self.base_url}/projects/{project_id}/files"
                    files_response = requests.get(files_url, headers=self.headers)
                    if files_response.status_code == 200:
                        project_files = files_response.json().get("files", [])
                        for file in project_files:
                            if query.lower() in file.get("name", "").lower():
                                files.append({
                                    "name": file.get("name"),
                                    "key": file.get("key"),
                                    "url": f"https://www.figma.com/file/{file.get('key')}"
                                })
            
            return files[:5]  # Limit to 5 results
        except Exception as e:
            print(f"Error searching files: {e}")
            return []
    
    def export_node_as_svg(self, file_key: str, node_id: str) -> Optional[str]:
        """Export a node as SVG"""
        try:
            url = f"{self.base_url}/images/{file_key}"
            params = {"ids": node_id, "format": "svg"}
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            export_data = response.json()
            export_url = export_data.get("images", {}).get(node_id)
            if not export_url:
                return None
            
            svg_response = requests.get(export_url)
            svg_response.raise_for_status()
            return svg_response.text
        except Exception as e:
            print(f"Error exporting SVG: {e}")
            return None

# Initialize clients
figma_client = FigmaClient()

@app.get("/")
async def root():
    return {"message": "Design & Research Assistant API"}

@app.post("/api/chat-simple", response_model=ChatResponse)
async def chat_simple(chat_message: ChatMessage):
    """Simple chat endpoint"""
    try:
        message = chat_message.message.lower()
        
        # Check if it's a file search request
        if any(keyword in message for keyword in ["figma", "file", "design", "search"]):
            files = figma_client.search_team_files(chat_message.message)
            if files:
                response_text = "Here are the Figma files I found:\n\n"
                for file in files:
                    response_text += f"• **{file['name']}**\n  [Open in Figma]({file['url']})\n\n"
            else:
                response_text = "I couldn't find any Figma files matching your search. Try a different search term."
            
            return ChatResponse(response=response_text)
        
        # Check if it's an export request
        export_keywords = ["export", "download", "get", "show me"]
        if any(keyword in message for keyword in export_keywords):
            # Simple export detection
            if "logo" in message:
                export_data = {
                    "node_name": "logo",
                    "node_id": "336:2901",  # Default logo node
                    "file_key": "3x616Uy5sRIDXcXHlNzyB7"
                }
                response_text = "I can export that for you! Click the download button below to get the logo."
                return ChatResponse(response=response_text, export_data=export_data)
        
        # Default response
        return ChatResponse(
            response="I'm the Design & Research Assistant! I can help you search Figma files and export assets. What would you like to do?"
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/export/figma")
async def export_figma(export_data: Dict[str, Any]):
    """Export Figma asset"""
    try:
        file_key = export_data.get("file_key")
        node_id = export_data.get("node_id")
        
        if not file_key or not node_id:
            raise HTTPException(status_code=400, detail="Missing file_key or node_id")
        
        svg_content = figma_client.export_node_as_svg(file_key, node_id)
        
        if not svg_content:
            raise HTTPException(status_code=404, detail="Could not export the asset")
        
        return {"svg_content": svg_content}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

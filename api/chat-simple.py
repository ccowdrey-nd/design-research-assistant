from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import requests
import re
import os
import json
import io
import base64

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
    conversation_history: Optional[List[Dict[str, Any]]] = []

class ChatResponse(BaseModel):
    response: str
    sources: Optional[List[str]] = []
    example_images: Optional[List[str]] = []
    export_data: Optional[Dict[str, Any]] = None

class ExportRequest(BaseModel):
    node_name: str
    node_id: Optional[str] = None
    color: Optional[str] = None

class FigmaClient:
    def __init__(self):
        self.api_token = os.getenv('FIGMA_API_TOKEN')
        self.team_id = os.getenv('FIGMA_TEAM_ID')
        self.base_url = "https://api.figma.com/v1"
        
    def _make_request(self, endpoint):
        """Make a request to the Figma API"""
        if not self.api_token:
            raise HTTPException(status_code=500, detail="Figma API token not configured")
        
        url = f"{self.base_url}{endpoint}"
        headers = {"X-Figma-Token": self.api_token}
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise HTTPException(status_code=500, detail=f"Figma API error: {str(e)}")
    
    def get_team_files(self):
        """Get all files from the team"""
        if not self.team_id:
            raise HTTPException(status_code=500, detail="Figma team ID not configured")
        
        endpoint = f"/teams/{self.team_id}/projects"
        projects = self._make_request(endpoint)
        
        all_files = []
        for project in projects.get('projects', []):
            project_id = project['id']
            files_endpoint = f"/projects/{project_id}/files"
            files = self._make_request(files_endpoint)
            all_files.extend(files.get('files', []))
        
        return all_files
    
    def search_files(self, query):
        """Search for files by name"""
        files = self.get_team_files()
        query_lower = query.lower()
        
        matching_files = []
        for file in files:
            if query_lower in file.get('name', '').lower():
                matching_files.append({
                    'name': file['name'],
                    'url': file['url'],
                    'last_modified': file.get('last_modified', ''),
                    'key': file['key']
                })
        
        return matching_files
    
    def get_file(self, file_key):
        """Get file details"""
        endpoint = f"/files/{file_key}"
        return self._make_request(endpoint)
    
    def search_node_by_name(self, file_key, node_name):
        """Search for a node by name in a file"""
        file_data = self.get_file(file_key)
        
        def search_nodes(nodes, target_name):
            results = []
            for node in nodes:
                if node.get('name', '').lower() == target_name.lower():
                    results.append(node)
                if 'children' in node:
                    results.extend(search_nodes(node['children'], target_name))
            return results
        
        if 'document' in file_data and 'children' in file_data['document']:
            return search_nodes(file_data['document']['children'], node_name)
        return []
    
    def export_node_as_svg(self, file_key, node_id, color=None):
        """Export a node as SVG"""
        endpoint = f"/files/{file_key}/nodes"
        params = {
            'ids': node_id,
            'format': 'svg'
        }
        
        if not self.api_token:
            raise HTTPException(status_code=500, detail="Figma API token not configured")
        
        url = f"{self.base_url}{endpoint}"
        headers = {"X-Figma-Token": self.api_token}
        
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            
            if 'nodes' in data and node_id in data['nodes']:
                svg_content = data['nodes'][node_id].get('image', '')
                if color and svg_content:
                    # Simple color replacement
                    svg_content = svg_content.replace('fill="#000000"', f'fill="{color}"')
                    svg_content = svg_content.replace('fill="#000"', f'fill="{color}"')
                return svg_content
            return None
        except requests.exceptions.RequestException as e:
            raise HTTPException(status_code=500, detail=f"Figma export error: {str(e)}")

# Initialize Figma client
figma_client = FigmaClient()

# Asset mapping for common requests
ASSET_MAP = {
    'primary logo': ('logo-nextdoor-wordmark-0513', '586:11968'),
    'logo': ('logo-nextdoor-wordmark-0513', '586:11968'),
    'house icon': ('logo-nextdoor', '336:2901'),
    'home icon': ('logo-nextdoor', '336:2901'),
    'chat icon': ('chat-right', '4087:39580'),
    'button': ('Button', None),
    'primary button': ('Button', None),
}

def is_export_request(message):
    """Check if the message is requesting an export"""
    export_keywords = [
        'export', 'download', 'get', 'show me', 'visual', 'visuals', 
        'examples', 'example', 'button', 'buttons', 'component', 'components',
        'logo', 'icon', 'symbol', 'graphic'
    ]
    
    message_lower = message.lower()
    return any(keyword in message_lower for keyword in export_keywords)

def extract_asset_name(message):
    """Extract asset name from user message"""
    # Remove common words
    clean_message = re.sub(r'\b(the|our|a|an|some|any)\b', '', message.lower())
    
    # Try to extract asset name using patterns
    patterns = [
        r'export\s+(?:the\s+|our\s+)?(.+?)(?:\s+in\s+|\s+with\s+|$)',
        r'download\s+(?:the\s+|our\s+)?(.+?)(?:\s+in\s+|\s+with\s+|$)',
        r'show\s+me\s+(?:the\s+|our\s+|a\s+)?(?:visual\s+of\s+(?:the\s+)?)?(.+?)(?:\s+in\s+|\s+with\s+|$)',
        r'get\s+(?:the\s+|our\s+)?(.+?)(?:\s+in\s+|\s+with\s+|$)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, clean_message)
        if match:
            asset_name = match.group(1).strip()
            # Clean up the asset name
            asset_name = re.sub(r'\s+(icon|component|graphic|symbol)$', '', asset_name)
            return asset_name.title()
    
    return None

def extract_color(message):
    """Extract color from user message"""
    color_patterns = [
        r'#([0-9A-Fa-f]{6})',
        r'#([0-9A-Fa-f]{3})',
        r'(lawn|green)',
        r'(dusk|blue)',
        r'(white)',
        r'(orange)',
        r'(purple)',
        r'(teal)',
    ]
    
    for pattern in color_patterns:
        match = re.search(pattern, message.lower())
        if match:
            color = match.group(1)
            if color in ['lawn', 'green']:
                return '#1B8751'
            elif color in ['dusk', 'blue']:
                return '#232F46'
            elif color == 'white':
                return '#FFFFFF'
            elif color == 'orange':
                return '#FF6B35'
            elif color == 'purple':
                return '#8B5CF6'
            elif color == 'teal':
                return '#14B8A6'
            elif len(color) == 6:
                return f'#{color}'
            elif len(color) == 3:
                return f'#{color[0]}{color[0]}{color[1]}{color[1]}{color[2]}{color[2]}'
    
    return None

@app.get("/")
async def root():
    return {"message": "Design & Research Assistant API"}

@app.post("/api/chat-simple", response_model=ChatResponse)
async def chat_simple(chat_message: ChatMessage):
    """Chat endpoint with full Figma integration"""
    message = chat_message.message
    
    # Check if user is asking about brand colors
    if any(keyword in message.lower() for keyword in ['brand color', 'brand colors', 'color palette', 'hex code', 'hex codes']):
        brand_colors_response = """
**Nextdoor Brand Colors:**

**Primary Colors:**
- **Lawn Green**: #1B8751
- **Dusk Blue**: #232F46
- **White**: #FFFFFF

**Secondary Colors:**
- **Light Gray**: #F5F5F5
- **Medium Gray**: #CCCCCC
- **Dark Gray**: #666666

**Accent Colors:**
- **Orange**: #FF6B35
- **Purple**: #8B5CF6
- **Teal**: #14B8A6

These colors are defined in our Brand Asset Kit and should be used consistently across all Nextdoor materials.
        """
        return ChatResponse(
            response=brand_colors_response.strip(),
            sources=["Brand Asset Kit"],
            example_images=[]
        )
    
    # Check if user is asking about latest files
    if any(keyword in message.lower() for keyword in ['latest files', 'recent files', 'new files', 'smb', 'figma file']):
        # Check if Figma API is configured
        if not os.getenv('FIGMA_API_TOKEN') or not os.getenv('FIGMA_TEAM_ID'):
            response = """**Figma Integration Not Configured**

To access your Figma files, you need to configure the following environment variables in Vercel:

1. **FIGMA_API_TOKEN** - Your Figma personal access token
2. **FIGMA_TEAM_ID** - Your Figma team ID
3. **FIGMA_BRAND_KIT_FILE_KEY** - Your Brand Asset Kit file key

**How to get these:**
- **API Token**: Go to Figma → Settings → Account → Personal Access Tokens
- **Team ID**: Found in your Figma team URL (figma.com/files/team/[TEAM_ID]/...)
- **File Key**: Found in your Brand Asset Kit URL (figma.com/file/[FILE_KEY]/...)

Once configured, I'll be able to search and export your Figma assets!"""
            
            return ChatResponse(
                response=response.strip(),
                sources=["Figma Setup Guide"],
                example_images=[]
            )
        
        try:
            files = figma_client.get_team_files()
            # Sort by last modified
            files.sort(key=lambda x: x.get('last_modified', ''), reverse=True)
            
            response = "**Latest Figma Files:**\n\n"
            sources = []
            for i, file in enumerate(files[:10]):  # Show top 10
                response += f"{i+1}. **{file['name']}**\n"
                response += f"   Last modified: {file.get('last_modified', 'Unknown')}\n"
                response += f"   URL: {file['url']}\n\n"
                sources.append(file['url'])
            
            return ChatResponse(
                response=response.strip(),
                sources=sources,
                example_images=[]
            )
        except Exception as e:
            return ChatResponse(
                response=f"I encountered an error fetching the latest files: {str(e)}",
                sources=[],
                example_images=[]
            )
    
    # Check if user is searching for files
    if any(keyword in message.lower() for keyword in ['search', 'find', 'look for', 'show me', 'smb', 'figma file']):
        try:
            # Extract search query
            search_query = message.lower()
            for word in ['search', 'find', 'look for', 'show me', 'files', 'figma file', 'what\'s the latest']:
                search_query = search_query.replace(word, '').strip()
            
            files = figma_client.search_files(search_query)
            
            if files:
                response = f"**Found {len(files)} files matching '{search_query}':**\n\n"
                sources = []
                for i, file in enumerate(files[:10]):  # Show top 10
                    response += f"{i+1}. **{file['name']}**\n"
                    response += f"   Last modified: {file.get('last_modified', 'Unknown')}\n"
                    response += f"   URL: {file['url']}\n\n"
                    sources.append(file['url'])
            else:
                response = f"No files found matching '{search_query}'"
                sources = []
            
            return ChatResponse(
                response=response.strip(),
                sources=sources,
                example_images=[]
            )
        except Exception as e:
            return ChatResponse(
                response=f"I encountered an error searching files: {str(e)}",
                sources=[],
                example_images=[]
            )
    
    # Check if user is requesting an export
    if is_export_request(message):
        try:
            asset_name = extract_asset_name(message)
            color = extract_color(message)
            
            if not asset_name:
                asset_name = "Button"  # Default fallback
            
            # Check asset map
            if asset_name.lower() in ASSET_MAP:
                node_name, node_id = ASSET_MAP[asset_name.lower()]
            else:
                node_name = asset_name
                node_id = None
            
            export_data = {
                'node_name': node_name,
                'node_id': node_id,
                'color': color
            }
            
            # Check if Figma API is configured
            if not os.getenv('FIGMA_API_TOKEN'):
                response = f"I can export that for you! Click the download button below to get the {asset_name.lower()}"
                if color:
                    response += f" in {color}"
                response += ".\n\n**Note:** Figma API is not configured, so this will download a placeholder SVG."
            else:
                response = f"I can export that for you! Click the download button below to get the {asset_name.lower()}"
                if color:
                    response += f" in {color}"
                response += "."
            
            return ChatResponse(
                response=response,
                sources=["Brand Asset Kit"],
                example_images=[],
                export_data=export_data
            )
        except Exception as e:
            return ChatResponse(
                response=f"I encountered an error processing your export request: {str(e)}",
                sources=[],
                example_images=[]
            )
    
    # Default response for other queries
    return ChatResponse(
        response="I'm the Design & Research Assistant! I can help you search Figma files and export assets. What would you like to do?",
        sources=[],
        example_images=[]
    )

@app.post("/api/export/figma")
async def export_figma(export_request: ExportRequest):
    """Export a Figma asset as SVG"""
    try:
        # Check if Figma API is configured
        if not os.getenv('FIGMA_API_TOKEN'):
            # Return a placeholder SVG
            placeholder_svg = f'''<svg width="200" height="100" xmlns="http://www.w3.org/2000/svg">
  <rect width="200" height="100" fill="#f0f0f0" stroke="#ccc" stroke-width="2"/>
  <text x="100" y="50" text-anchor="middle" font-family="Arial, sans-serif" font-size="14" fill="#666">
    {export_request.node_name}
  </text>
  <text x="100" y="70" text-anchor="middle" font-family="Arial, sans-serif" font-size="10" fill="#999">
    Placeholder - Configure Figma API
  </text>
</svg>'''
            
            return StreamingResponse(
                io.BytesIO(placeholder_svg.encode()),
                media_type="image/svg+xml",
                headers={"Content-Disposition": f"attachment; filename={export_request.node_name}.svg"}
            )
        
        # Use Brand Asset Kit file key (you'll need to set this)
        brand_kit_file_key = os.getenv('FIGMA_BRAND_KIT_FILE_KEY', '3x616Uy5sRIDXcXHlNzyB7')
        
        if not export_request.node_id:
            # Search for the node by name
            nodes = figma_client.search_node_by_name(brand_kit_file_key, export_request.node_name)
            if not nodes:
                raise HTTPException(status_code=404, detail=f"Node '{export_request.node_name}' not found")
            node_id = nodes[0]['id']
        else:
            node_id = export_request.node_id
        
        # Export the node
        svg_content = figma_client.export_node_as_svg(brand_kit_file_key, node_id, export_request.color)
        
        if not svg_content:
            raise HTTPException(status_code=404, detail="Failed to export SVG")
        
        # Return the SVG content
        return StreamingResponse(
            io.BytesIO(svg_content.encode()),
            media_type="image/svg+xml",
            headers={"Content-Disposition": f"attachment; filename={export_request.node_name}.svg"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
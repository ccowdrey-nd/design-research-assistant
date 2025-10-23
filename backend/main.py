"""
Main FastAPI application for the design assistant chatbot.
"""
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, Response
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import json
from openai import OpenAI
import re

from config import settings
from auth import get_current_user
from integrations.figma import figma_client
from integrations.google_slides import google_slides_client
from rag.embeddings import embedding_manager
from rag.retrieval import retrieval_manager
from analyzer import brand_analyzer


# Initialize FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="Design assistant chatbot with RAG and brand compliance analysis",
    version="1.0.0"
)

# Configure CORS
allowed_origins = settings.allowed_origins.split(',')
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize OpenAI client
openai_client = OpenAI(api_key=settings.openai_api_key)


# Pydantic models
class ChatMessage(BaseModel):
    message: str
    conversation_history: Optional[List[Dict[str, str]]] = []


class ChatResponse(BaseModel):
    response: str
    sources: List[Dict[str, Any]]
    export_data: Optional[Dict[str, Any]] = None
    example_images: Optional[List[str]] = None


class SyncRequest(BaseModel):
    force: bool = False


class AnalysisResponse(BaseModel):
    analysis: str
    sources: List[Dict[str, Any]]
    recommendations: List[str]


class ExportRequest(BaseModel):
    node_name: str
    node_id: Optional[str] = None  # Explicit node ID if known
    file_key: Optional[str] = None
    color: Optional[str] = None  # Hex color like "#1B8751"


# Health check endpoint
@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "services": {
            "openai": bool(settings.openai_api_key),
            "figma": bool(settings.figma_access_token),
            "google_slides": bool(settings.google_application_credentials),
        }
    }


# Chat endpoint with streaming
@app.post("/api/chat")
async def chat(
    chat_message: ChatMessage,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Main chat endpoint with RAG and streaming response.
    """
    try:
        # Enhance queries about specific colors to get better results
        enhanced_query = chat_message.message
        if any(keyword in chat_message.message.lower() for keyword in ['hex', 'color', 'vista', 'blue ridge', 'dusk', 'lawn', 'plaster', 'dew', 'pine']):
            enhanced_query = chat_message.message + " brand colors palette"
        
        # Build context from retrieved documents
        context = retrieval_manager.build_context(enhanced_query)
        
        # Get source citations
        sources = retrieval_manager.get_sources(enhanced_query)
        
        # Check if user is asking for a Figma file link
        figma_files_context = ""
        message_lower = chat_message.message.lower()
        should_search_files = any(keyword in message_lower for keyword in [
            'figma file', 'link to', 'file called', 'file named', 'show me the file',
            'send me', 'share the', 'find the file', 'link for', 'where is the', 'file?'
        ])
        
        if should_search_files:
            # Search for files using all significant words in the query
            words = [w.strip('?.,!') for w in chat_message.message.split() if len(w) > 3]
            all_results = {}
            for word in words[:5]:  # Check first 5 significant words
                file_results = figma_client.search_team_files(word)
                for file in file_results:
                    all_results[file['key']] = file
            
            if all_results:
                figma_files_context += f"\n\nAvailable Figma files:\n"
                for file in list(all_results.values())[:10]:
                    figma_files_context += f"- {file['name']}: {file['url']}\n"
        
        # Build system prompt
        system_prompt = f"""You are a helpful design system assistant for Nextdoor's design team.
You have access to the company's design system from Figma and documentation from Google Slides.

Use the following context to answer questions accurately:

{context}

{figma_files_context}

When answering:
- Be specific and reference the design system when applicable
- Cite sources when providing information
- Provide actionable guidance
- If asked for a Figma file link, provide the full URL from the available Figma files listed above
- If you're not sure, say so rather than guessing
- Format your responses clearly with markdown

User: {current_user.get('name', 'Unknown')} ({current_user.get('email', 'Unknown')})
"""
        
        # Build messages for OpenAI
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add conversation history
        for msg in chat_message.conversation_history[-5:]:  # Last 5 messages
            messages.append({
                "role": msg.get("role", "user"),
                "content": msg.get("content", "")
            })
        
        # Add current message
        messages.append({"role": "user", "content": chat_message.message})
        
        # Stream response
        async def generate():
            stream = openai_client.chat.completions.create(
                model=settings.chat_model,
                messages=messages,
                temperature=settings.temperature,
                max_tokens=settings.max_tokens,
                stream=True
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield f"data: {json.dumps({'content': chunk.choices[0].delta.content})}\n\n"
            
            # Send sources at the end
            yield f"data: {json.dumps({'sources': sources})}\n\n"
            yield "data: [DONE]\n\n"
        
        return StreamingResponse(generate(), media_type="text/event-stream")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Non-streaming chat endpoint (alternative)
@app.post("/api/chat-simple")
async def chat_simple(
    chat_message: ChatMessage,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Simple non-streaming chat endpoint."""
    try:
        # Enhance queries for better retrieval
        message_lower = chat_message.message.lower()
        enhanced_query = chat_message.message
        
        # Color queries
        if any(keyword in message_lower for keyword in ['hex', 'color', 'vista', 'blue ridge', 'dusk', 'lawn', 'plaster', 'dew', 'pine']):
            enhanced_query = chat_message.message + " brand colors palette"
        
        # Organizational queries
        if any(keyword in message_lower for keyword in ['who owns', 'who is', 'head of', 'leader', 'team structure', 'organization', 'org chart', 'reports to', 'design team']):
            enhanced_query = chat_message.message + " design and research organization team map consumer advertising nextdoor"
        
        # UXR/Research queries - search with broader context
        if any(keyword in message_lower for keyword in ['research', 'uxr', 'user research', 'insights', 'findings', 'learned', 'users say', 'feedback', 'pain points', 'user needs']):
            enhanced_query = chat_message.message + " research insights findings user feedback"
        
        # Check if asking for visual examples
        examples_context = ""
        example_images = []
        show_visual_examples = 'example' in message_lower or 'show me' in message_lower
        
        if show_visual_examples:
            if 'email' in message_lower or 'smb' in message_lower:
                email_examples = retrieval_manager.search_examples("email", top_k=3)
                if email_examples['documents']:
                    examples_context += "\n\nApproved Email Examples:\n"
                    for meta in email_examples['metadatas']:
                        examples_context += f"- {meta.get('name', 'Unnamed')}: {meta.get('url', '')}\n"
                    
                    # Try to export first example as image
                    try:
                        # Get a frame from the email creative file
                        frame_id = figma_client.get_frame_by_name("HU0Fiwou6ZpIrnxuRixJV0", "template")
                        if not frame_id:
                            # Try other common names
                            frame_id = figma_client.get_frame_by_name("HU0Fiwou6ZpIrnxuRixJV0", "email")
                        
                        if frame_id:
                            image_url = figma_client.export_node_as_image("HU0Fiwou6ZpIrnxuRixJV0", frame_id)
                            if image_url:
                                example_images.append(image_url)
                    except Exception as e:
                        print(f"Error exporting email example: {e}")
            
            if 'ad' in message_lower or 'social' in message_lower or 'paid' in message_lower:
                ad_examples = retrieval_manager.search_examples("ad", top_k=3)
                if ad_examples['documents']:
                    examples_context += "\n\nApproved Ad Templates:\n"
                    for meta in ad_examples['metadatas']:
                        examples_context += f"- {meta.get('name', 'Unnamed')}: {meta.get('url', '')}\n"
                    
                    # Try to export first example as image
                    try:
                        # Get a frame from the paid ad templates file
                        frame_id = figma_client.get_frame_by_name("5NHfO3JiYYNeuFAz7Ug4kJ", "option 1")
                        if not frame_id:
                            frame_id = figma_client.get_frame_by_name("5NHfO3JiYYNeuFAz7Ug4kJ", "template")
                        
                        if frame_id:
                            image_url = figma_client.export_node_as_image("5NHfO3JiYYNeuFAz7Ug4kJ", frame_id)
                            if image_url:
                                example_images.append(image_url)
                    except Exception as e:
                        print(f"Error exporting ad example: {e}")
        
        context = retrieval_manager.build_context(enhanced_query)
        if examples_context:
            context += examples_context
        
        sources = retrieval_manager.get_sources(enhanced_query)
        
        # Check if user is asking for a Figma file link or recent files
        figma_files_context = ""
        message_lower = chat_message.message.lower()
        
        # Check for recent/latest files queries
        is_recent_files_query = any(keyword in message_lower for keyword in [
            'latest', 'recent', 'recently', 'last edited', 'last modified', 
            'most recent', 'newest', 'current', 'up to date'
        ])
        
        should_search_files = any(keyword in message_lower for keyword in [
            'figma file', 'link to', 'file called', 'file named', 'show me the file',
            'send me', 'share the', 'find the file', 'link for', 'where is the', 'file?'
        ])
        
        if is_recent_files_query or should_search_files:
            all_results = {}
            
            if is_recent_files_query:
                # Get fresh file metadata from Figma for recent files queries
                print("Fetching recent files from Figma...")
                fresh_files = figma_client.get_all_team_files_with_metadata(settings.figma_team_id)
                
                # Sort by last_modified, most recent first
                fresh_files.sort(key=lambda x: x.get('last_modified', ''), reverse=True)
                
                # Take top 15 most recent files
                for file in fresh_files[:15]:
                    all_results[file['key']] = file
                    
                figma_files_context += f"\n\nMost recently modified Figma files (sorted by last_modified date, newest first):\n"
            else:
                # Regular file search by name
                words = [w.strip('?.,!') for w in chat_message.message.split() if len(w) > 3]
                for word in words[:5]:  # Check first 5 significant words
                    file_results = figma_client.search_team_files(word)
                    for file in file_results:
                        all_results[file['key']] = file
            
            if all_results:
                if not is_recent_files_query:
                    figma_files_context += f"\n\nAvailable Figma files:\n"
                for file in list(all_results.values())[:10]:
                    figma_files_context += f"- {file['name']} (last modified: {file.get('last_modified', 'unknown')})\n"
                    figma_files_context += f"  Project: {file.get('project', 'Unknown')}\n"
                    figma_files_context += f"  URL: {file['url']}\n"
        
        system_prompt = f"""You are a helpful design system assistant for Nextdoor's design team.

Context from design system:
{context}

{figma_files_context}

When answering:
- Provide clear, accurate answers based on the design system
- If asked about UXR insights, research findings, or user feedback:
  * Synthesize findings from multiple sources if available
  * Quote specific insights and data points
  * Reference which research deck/slide each finding came from
  * Provide links to the original presentation slides
  * Organize findings into themes or categories
- If asked about design team organization, ownership, or leadership, check the context above for "Nextdoor Design and Research Organization" content and reference it
- If the org structure is in the context but doesn't have specific names, explain what team areas exist (Consumer Team, Advertising Experience, etc.) based on the information provided
- If asked for a Figma file link, provide the full URL from the available Figma files listed above
- If asked about "latest" or "recent" files, use the file list above which is sorted by last_modified date (newest first). Show the file name, when it was last modified, and provide the link. Note: The Figma API doesn't provide information about WHO edited files, only WHEN they were last modified.
- If asked to export/download ANY asset from the Brand Asset Kit (logo, icon, symbol, graphic, button, component, illustration, etc.) or show visuals/examples, ALWAYS respond positively:
  * For logo requests: "I can export that for you! Click the download button below to get the [asset name] in [color if specified]."
  * For button/component requests: "I can export that for you! Click the download button below to get visual examples of the buttons in various sizes, colors, and states."
  * For icon requests: "I can export that for you! Click the download button below to get the [icon name] in [color if specified]."
  * For any other asset: "I can export that for you! Click the download button below to get the [asset name]."
  The system can export ANY asset from the Brand Asset Kit - it will automatically search for and find the asset by name.
  The download button will appear automatically - you just need to confirm the export is ready.
  Even if you're not 100% sure the exact asset name, confirm the export - the system uses fuzzy matching to find the asset.
- Be helpful and specific"""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": chat_message.message}
        ]
        
        response = openai_client.chat.completions.create(
            model=settings.chat_model,
            messages=messages,
            temperature=settings.temperature,
            max_tokens=settings.max_tokens
        )
        
        # Check if this is an export request
        export_data = None
        message_lower = chat_message.message.lower()
        
        is_export_request = any(keyword in message_lower for keyword in [
            'export', 'download', 'give me the', 'looking to download', 'get me the',
            'show me', 'visual', 'visuals', 'examples', 'example', 'button', 'buttons',
            'component', 'components', 'logo', 'logos', 'icon', 'icons'
        ])
        
        if is_export_request:
            # Detect what asset is being requested
            node_name = None
            export_color = None
            
            # Common asset mapping for known aliases with specific node IDs
            # Order matters - check longer/more specific phrases first
            # Format: (search_term, (node_name, node_id))
            asset_map = [
                ('primary logo', ('logo-nextdoor-wordmark-0513', '586:11968')),  # Full logo with wordmark
                ('nextdoor logo', ('logo-nextdoor-wordmark-0513', '586:11968')),
                ('full logo', ('logo-nextdoor-wordmark-0513', '586:11968')),
                ('house icon', ('logo-nextdoor', '336:2901')),  # Just the house symbol
                ('house symbol', ('logo-nextdoor', '336:2901')),
                ('home icon', ('logo-nextdoor', '336:2901')),  # Alternative name for house icon
                ('home symbol', ('logo-nextdoor', '336:2901')),
                ('chat icon', ('chat-right', '4087:39580')),  # Chat message icon
                ('symbol', ('logo-nextdoor', '336:2901')),
                ('wordmark', ('logo-nextdoor-wordmark-0513', '586:11968')),  # Use full logo for wordmark requests
            ]
            
            # Try to identify the asset from the message using known aliases
            node_id = None
            for term, asset_data in asset_map:
                if term in message_lower:
                    node_name, node_id = asset_data  # Unpack tuple (name, id)
                    break
            
            # If no match found, try to extract asset name from the message dynamically
            if node_name is None:
                # Extract asset name using regex patterns
                patterns = [
                    r'export (?:the |our )?(.+?)(?:\s+in\s+|\s+with\s+|$)',  # "export the X" or "export X in lawn"
                    r'download (?:the |our )?(.+?)(?:\s+in\s+|\s+with\s+|$)',  # "download the X"
                    r'get me (?:the |our )?(.+?)(?:\s+in\s+|\s+with\s+|$)',  # "get me the X"
                    r'show me (?:the |our |a )?(?:visual of (?:the )?)?(.+?)(?:\s+in\s+|\s+with\s+|$)',  # "show me visual of X"
                    r'(?:visual|example) of (?:the )?(.+?)(?:\s+in\s+|\s+with\s+|$)',  # "visual of X"
                ]
                
                for pattern in patterns:
                    match = re.search(pattern, message_lower, re.IGNORECASE)
                    if match:
                        extracted = match.group(1).strip()
                        # Clean up common words and extra whitespace
                        extracted = re.sub(r'\b(the|our|a|an|from|brand|kit|asset)\b', '', extracted, flags=re.IGNORECASE).strip()
                        # Remove trailing words like "icon", "component", etc.
                        extracted = re.sub(r'\s+(icon|icons|component|components|graphic|graphics)$', '', extracted, flags=re.IGNORECASE).strip()
                        # Remove trailing punctuation
                        extracted = re.sub(r'[?.!,;]+$', '', extracted).strip()
                        # Remove extra spaces
                        extracted = ' '.join(extracted.split())
                        if extracted and len(extracted) > 2:  # Make sure we have a meaningful name
                            # Keep the original casing for better Figma matching (many icons use lowercase with hyphens)
                            node_name = extracted
                            break
            
            # If still no match, default based on keywords
            if node_name is None:
                if any(word in message_lower for word in ['visual', 'example', 'component', 'button']):
                    node_name = 'Button'
                elif any(word in message_lower for word in ['logo']):
                    node_name = 'Primary Logo'
                elif any(word in message_lower for word in ['icon']):
                    node_name = 'House Icon'
                else:
                    node_name = 'Primary Logo'  # Default to logo for generic exports
            
            # Look for color names and convert to hex
            color_map = {
                'lawn': '#1B8751',
                'dusk': '#232F46',
                'vista blue': '#85AFCC',
                'blue ridge': '#47608E',
                'pine': '#0A402E',
                'dew': '#ADD9B8',
                'plaster': '#F0F2F5'
            }
            
            for color_name, hex_code in color_map.items():
                if color_name in message_lower:
                    export_color = hex_code
                    break
            
            # Check for hex codes in the message
            hex_match = re.search(r'#[0-9A-Fa-f]{6}', chat_message.message)
            if hex_match:
                export_color = hex_match.group(0)
            
            # If we don't have a node_id from the asset map, try fuzzy search
            if node_id is None:
                node_id = figma_client.search_node_by_name("3x616Uy5sRIDXcXHlNzyB7", node_name)
            
            export_data = {
                "node_name": node_name,
                "node_id": node_id,  # Include node_id if we have it from the asset map or fuzzy search
                "color": export_color,
                "file_key": "3x616Uy5sRIDXcXHlNzyB7"
            }
            
            print(f"Export request detected. Node name: {node_name}, Node ID: {node_id}, Color: {export_color}")
        
        return {
            "response": response.choices[0].message.content,
            "sources": sources,
            "export_data": export_data,
            "example_images": example_images if example_images else None
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Image analysis endpoint
@app.post("/api/analyze-image", response_model=AnalysisResponse)
async def analyze_image(
    file: UploadFile = File(...),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Analyze uploaded image for brand compliance.
    """
    try:
        # Read image data
        image_data = await file.read()
        
        # Validate image
        if not brand_analyzer.validate_image(image_data):
            raise HTTPException(status_code=400, detail="Invalid image file")
        
        # Analyze image
        result = brand_analyzer.analyze_image(
            image_data=image_data,
            image_type=file.content_type or "image/png"
        )
        
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Sync Figma files
@app.post("/api/sync/figma")
async def sync_figma(
    sync_request: SyncRequest = SyncRequest(),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Sync Figma files to the vector database.
    Indexes ALL team files as metadata, plus full content for key files.
    """
    try:
        synced_files = []
        all_files = []
        
        # First, index all team files as metadata for searchability
        if settings.figma_team_id:
            print("Indexing all team files metadata...")
            all_files = figma_client.get_all_team_files_with_metadata(settings.figma_team_id)
            embedding_manager.add_figma_file_metadata(all_files)
            print(f"Indexed {len(all_files)} file metadata entries")
        
        # Get file keys for full content sync (priority files)
        file_keys = []
        if settings.figma_file_keys:
            file_keys = settings.figma_file_keys.split(',')
        
        if not file_keys:
            # If no specific files, just return metadata sync results
            return {
                "status": "success",
                "message": f"Indexed {len(all_files)} files as searchable metadata",
                "synced_files": [],
                "total_documents": embedding_manager.get_collection_stats()['total_documents']
            }
        
        # Process each file
        for file_key in file_keys[:10]:  # Limit to 10 files for now
            file_key = file_key.strip()
            
            # Extract design tokens
            tokens = figma_client.extract_design_tokens(file_key)
            embedding_manager.add_figma_styles(tokens)
            
            # Extract components
            components = figma_client.extract_component_info(file_key)
            embedding_manager.add_figma_components(components, file_key)
            
            # Extract page content (for brand kits and documentation)
            page_content = figma_client.extract_page_content(file_key)
            embedding_manager.add_figma_page_content(page_content)
            
            synced_files.append({
                "file_key": file_key,
                "name": tokens.get('file_name', 'Unknown'),
                "components": len(components),
                "styles": len(tokens.get('colors', [])) + len(tokens.get('typography', [])),
                "pages": len(page_content)
            })
        
        stats = embedding_manager.get_collection_stats()
        
        return {
            "status": "success",
            "message": f"Indexed {len(all_files) if settings.figma_team_id else 0} files as metadata, synced {len(synced_files)} files with full content",
            "synced_files": synced_files,
            "total_files_indexed": len(all_files) if settings.figma_team_id else 0,
            "total_documents": stats['total_documents']
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Sync Google Slides
@app.post("/api/sync/slides")
async def sync_slides(
    sync_request: SyncRequest = SyncRequest(),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Sync Google Slides presentations to the vector database.
    """
    try:
        # Get all presentations
        presentations = google_slides_client.get_all_presentations_content()
        
        synced_presentations = []
        
        # Process each presentation
        for pres in presentations:
            embedding_manager.add_slides_content(pres)
            synced_presentations.append({
                "name": pres.get('name', 'Unknown'),
                "slides": len(pres.get('slides', []))
            })
        
        stats = embedding_manager.get_collection_stats()
        
        return {
            "status": "success",
            "synced_presentations": synced_presentations,
            "total_documents": stats['total_documents']
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Get collection stats
@app.get("/api/stats")
async def get_stats(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get statistics about the vector database."""
    stats = embedding_manager.get_collection_stats()
    return stats


# Search endpoint (for testing)
@app.post("/api/search")
async def search(
    query: str,
    top_k: int = 5,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Search the design system."""
    results = retrieval_manager.search(query, top_k=top_k)
    return results


# Search Figma files by name
@app.get("/api/figma/search")
async def search_figma_files(
    query: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Search for Figma files by name.
    """
    try:
        results = figma_client.search_team_files(query)
        return {
            "query": query,
            "results": results,
            "count": len(results)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Export asset from Figma
@app.post("/api/export/figma")
async def export_figma_asset(
    export_request: ExportRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Export an asset from Figma as SVG, optionally with color change.
    """
    try:
        # Default to Brand Asset Kit if no file specified
        file_key = export_request.file_key or "3x616Uy5sRIDXcXHlNzyB7"
        
        # Use provided node_id or search for it by name
        if export_request.node_id:
            node_id = export_request.node_id
        else:
            node_id = figma_client.search_node_by_name(file_key, export_request.node_name)
        
        if not node_id:
            raise HTTPException(
                status_code=404,
                detail=f"Could not find '{export_request.node_name}' in the Figma file"
            )
        
        # Export as SVG
        svg_content = figma_client.export_node_as_svg(file_key, node_id)
        
        if not svg_content:
            raise HTTPException(
                status_code=500,
                detail="Failed to export SVG from Figma"
            )
        
        # Change color if requested
        if export_request.color:
            svg_content = figma_client.change_svg_color(svg_content, export_request.color)
        
        # Clean filename
        filename = re.sub(r'[^a-zA-Z0-9-_]', '-', export_request.node_name.lower())
        
        # Return SVG file
        return Response(
            content=svg_content,
            media_type="image/svg+xml",
            headers={
                "Content-Disposition": f"attachment; filename={filename}.svg"
            }
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


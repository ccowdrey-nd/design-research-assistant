"""
Figma API integration for fetching design files, components, and styles.
"""
import requests
from typing import List, Dict, Any, Optional
from config import settings


class FigmaClient:
    """Client for interacting with Figma API."""
    
    BASE_URL = "https://api.figma.com/v1"
    
    def __init__(self, access_token: Optional[str] = None):
        self.access_token = access_token or settings.figma_access_token
        self.headers = {
            "X-Figma-Token": self.access_token,
        }
        self._file_cache: Optional[List[Dict[str, Any]]] = None
        self._cache_timestamp: Optional[float] = None
        self._cache_ttl = 3600  # Cache for 1 hour
    
    def get_file(self, file_key: str) -> Dict[str, Any]:
        """
        Fetch a Figma file's structure.
        
        Args:
            file_key: The Figma file key
            
        Returns:
            File data including document structure
        """
        url = f"{self.BASE_URL}/files/{file_key}"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def get_file_components(self, file_key: str) -> Dict[str, Any]:
        """
        Fetch components from a Figma file.
        
        Args:
            file_key: The Figma file key
            
        Returns:
            Component metadata
        """
        url = f"{self.BASE_URL}/files/{file_key}/components"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def get_file_styles(self, file_key: str) -> Dict[str, Any]:
        """
        Fetch styles from a Figma file.
        
        Args:
            file_key: The Figma file key
            
        Returns:
            Style metadata including colors, text styles, etc.
        """
        url = f"{self.BASE_URL}/files/{file_key}/styles"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def get_team_projects(self, team_id: str) -> Dict[str, Any]:
        """
        Fetch all projects in a team.
        
        Args:
            team_id: The Figma team ID
            
        Returns:
            List of projects
        """
        url = f"{self.BASE_URL}/teams/{team_id}/projects"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def get_project_files(self, project_id: str) -> Dict[str, Any]:
        """
        Fetch all files in a project.
        
        Args:
            project_id: The Figma project ID
            
        Returns:
            List of files in the project
        """
        url = f"{self.BASE_URL}/projects/{project_id}/files"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def extract_design_tokens(self, file_key: str) -> Dict[str, Any]:
        """
        Extract design tokens (colors, typography, spacing) from a Figma file.
        
        Args:
            file_key: The Figma file key
            
        Returns:
            Structured design tokens
        """
        file_data = self.get_file(file_key)
        styles = self.get_file_styles(file_key)
        
        tokens = {
            "colors": [],
            "typography": [],
            "effects": [],
            "file_name": file_data.get("name", ""),
            "file_key": file_key,
            "last_modified": file_data.get("lastModified", ""),
        }
        
        # Extract color styles
        styles_data = styles.get("meta", {}).get("styles", {})
        
        # Handle both dict and list responses from Figma API
        if isinstance(styles_data, dict):
            styles_list = [(style_id, style_meta) for style_id, style_meta in styles_data.items()]
        else:
            styles_list = [(str(i), style) for i, style in enumerate(styles_data)]
        
        for style_id, style_meta in styles_list:
            style_type = style_meta.get("style_type")
            if style_type == "FILL":
                tokens["colors"].append({
                    "id": style_id,
                    "name": style_meta.get("name", ""),
                    "description": style_meta.get("description", ""),
                })
            elif style_type == "TEXT":
                tokens["typography"].append({
                    "id": style_id,
                    "name": style_meta.get("name", ""),
                    "description": style_meta.get("description", ""),
                })
            elif style_type == "EFFECT":
                tokens["effects"].append({
                    "id": style_id,
                    "name": style_meta.get("name", ""),
                    "description": style_meta.get("description", ""),
                })
        
        return tokens
    
    def extract_component_info(self, file_key: str) -> List[Dict[str, Any]]:
        """
        Extract component information from a Figma file.
        
        Args:
            file_key: The Figma file key
            
        Returns:
            List of component information
        """
        components_data = self.get_file_components(file_key)
        components = []
        
        components_raw = components_data.get("meta", {}).get("components", {})
        
        # Handle both dict and list responses from Figma API
        if isinstance(components_raw, dict):
            components_list = [(comp_id, comp_meta) for comp_id, comp_meta in components_raw.items()]
        else:
            components_list = [(str(i), comp) for i, comp in enumerate(components_raw)]
        
        for comp_id, comp_meta in components_list:
            components.append({
                "id": comp_id,
                "name": comp_meta.get("name", ""),
                "description": comp_meta.get("description", ""),
                "component_set_id": comp_meta.get("containing_frame", {}).get("nodeId"),
                "file_key": file_key,
            })
        
        return components
    
    def extract_text_content(self, node: Dict[str, Any], texts: List[str]) -> None:
        """
        Recursively extract text content from Figma nodes.
        
        Args:
            node: Figma node dictionary
            texts: List to accumulate text content
        """
        if node.get("type") == "TEXT":
            characters = node.get("characters", "")
            if characters:
                texts.append(characters)
        
        # Recursively process children
        for child in node.get("children", []):
            self.extract_text_content(child, texts)
    
    def extract_page_content(self, file_key: str) -> List[Dict[str, Any]]:
        """
        Extract all page content including text, frames, and structure.
        
        Args:
            file_key: The Figma file key
            
        Returns:
            List of page content dictionaries
        """
        file_data = self.get_file(file_key)
        pages_content = []
        file_name = file_data.get("name", "")
        
        # Detect content type from file name
        content_category = "general"
        if "email" in file_name.lower():
            content_category = "email_example"
        elif "ad" in file_name.lower() or "paid" in file_name.lower():
            content_category = "ad_example"
        
        for page in file_data.get("document", {}).get("children", []):
            page_name = page.get("name", "Untitled Page")
            texts = []
            
            # Extract all text from this page
            self.extract_text_content(page, texts)
            
            # Combine all text from the page
            page_text = "\n".join(texts)
            
            # Determine if this page contains examples
            is_example = False
            example_type = None
            
            if "email" in page_name.lower() or "email" in file_name.lower():
                is_example = True
                example_type = "email"
            elif "ad" in page_name.lower() or "template" in page_name.lower():
                is_example = True
                example_type = "ad"
            
            if page_text.strip():
                pages_content.append({
                    "page_name": page_name,
                    "content": page_text,
                    "file_key": file_key,
                    "file_name": file_name,
                    "is_example": is_example,
                    "example_type": example_type,
                    "content_category": content_category,
                })
        
        return pages_content
    
    def get_all_team_files(self, team_id: Optional[str] = None) -> List[str]:
        """
        Get all file keys from a team.
        
        Args:
            team_id: The Figma team ID (uses config if not provided)
            
        Returns:
            List of file keys
        """
        team_id = team_id or settings.figma_team_id
        if not team_id:
            return []
        
        file_keys = []
        projects = self.get_team_projects(team_id)
        
        for project in projects.get("projects", []):
            project_files = self.get_project_files(project["id"])
            for file in project_files.get("files", []):
                file_keys.append(file["key"])
        
        return file_keys
    
    def get_all_team_files_with_metadata(self, team_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get all files from team with metadata for indexing.
        
        Args:
            team_id: The Figma team ID (uses config if not provided)
            
        Returns:
            List of file metadata dictionaries
        """
        team_id = team_id or settings.figma_team_id
        if not team_id:
            return []
        
        all_files = []
        projects = self.get_team_projects(team_id)
        
        for project in projects.get("projects", []):
            project_name = project.get("name", "")
            project_files = self.get_project_files(project["id"])
            
            for file in project_files.get("files", []):
                all_files.append({
                    "key": file["key"],
                    "name": file.get("name", ""),
                    "project": project_name,
                    "url": f"https://www.figma.com/design/{file['key']}/{file.get('name', '').replace(' ', '-')}",
                    "last_modified": file.get("last_modified", ""),
                    "thumbnail_url": file.get("thumbnail_url", "")
                })
        
        return all_files
    
    def _get_all_files_cached(self, team_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get all files from team with caching.
        
        Args:
            team_id: The Figma team ID
            
        Returns:
            Cached list of all files
        """
        import time
        
        team_id = team_id or settings.figma_team_id
        if not team_id:
            return []
        
        # Check if cache is valid
        current_time = time.time()
        if (self._file_cache is not None and 
            self._cache_timestamp is not None and 
            current_time - self._cache_timestamp < self._cache_ttl):
            return self._file_cache
        
        # Build new cache
        all_files = []
        projects = self.get_team_projects(team_id)
        
        for project in projects.get("projects", []):
            project_files = self.get_project_files(project["id"])
            for file in project_files.get("files", []):
                all_files.append({
                    "key": file["key"],
                    "name": file.get("name", ""),
                    "project": project.get("name", ""),
                    "url": f"https://www.figma.com/design/{file['key']}/{file.get('name', '').replace(' ', '-')}",
                    "last_modified": file.get("last_modified", "")
                })
        
        # Update cache
        self._file_cache = all_files
        self._cache_timestamp = current_time
        
        return all_files
    
    def search_team_files(self, query: str, team_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Search for Figma files by name in the team (uses caching for speed).
        
        Args:
            query: Search term to match against file names
            team_id: The Figma team ID (uses config if not provided)
            
        Returns:
            List of matching files with their details
        """
        all_files = self._get_all_files_cached(team_id)
        
        query_lower = query.lower()
        matching_files = [
            file for file in all_files 
            if query_lower in file['name'].lower()
        ]
        
        return matching_files
    
    def export_node_as_svg(self, file_key: str, node_id: str) -> Optional[str]:
        """
        Export a specific node as SVG from Figma.
        If the node is an INSTANCE, automatically finds and exports the VECTOR child.
        
        Args:
            file_key: The Figma file key
            node_id: The node ID to export
            
        Returns:
            SVG content as string, or None if failed
        """
        # First, try to export the node as-is
        try:
            svg_content = self._export_node_as_svg_direct(file_key, node_id)
            if svg_content and len(svg_content.strip()) > 100:  # Check if we got meaningful content
                return svg_content
        except:
            pass
        
        # If that failed or returned minimal content, check if it's an INSTANCE
        # and try to find a VECTOR child
        try:
            file_data = self.get_file(file_key)
            node = self._find_node_by_id(file_data.get("document", {}), node_id)
            
            if node and node.get("type") == "INSTANCE":
                # Look for VECTOR children
                vector_children = self._find_vector_children(node)
                for vector_id in vector_children:
                    try:
                        svg_content = self._export_node_as_svg_direct(file_key, vector_id)
                        if svg_content and len(svg_content.strip()) > 100:
                            return svg_content
                    except:
                        continue
        except:
            pass
        
        # If all else fails, try the original node one more time
        try:
            return self._export_node_as_svg_direct(file_key, node_id)
        except:
            return None
    
    def _export_node_as_svg_direct(self, file_key: str, node_id: str) -> Optional[str]:
        """Direct export without fallback logic."""
        # Request image export
        url = f"{self.BASE_URL}/images/{file_key}"
        params = {
            "ids": node_id,
            "format": "svg"
        }
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        
        # Get the export URL
        export_data = response.json()
        export_url = export_data.get("images", {}).get(node_id)
        
        if not export_url:
            return None
        
        # Download the SVG
        svg_response = requests.get(export_url)
        svg_response.raise_for_status()
        
        return svg_response.text
    
    def _find_node_by_id(self, node, target_id):
        """Find a node by ID recursively."""
        if node.get('id') == target_id:
            return node
        if 'children' in node:
            for child in node['children']:
                result = self._find_node_by_id(child, target_id)
                if result:
                    return result
        return None
    
    def _find_vector_children(self, node):
        """Find all VECTOR children of a node."""
        vector_ids = []
        if 'children' in node:
            for child in node['children']:
                if child.get('type') == 'VECTOR':
                    vector_ids.append(child.get('id'))
                # Also check nested children
                vector_ids.extend(self._find_vector_children(child))
        return vector_ids
    
    def export_node_as_image(self, file_key: str, node_id: str, scale: int = 2) -> Optional[str]:
        """
        Export a specific node as PNG image from Figma and return the URL.
        
        Args:
            file_key: The Figma file key
            node_id: The node ID to export
            scale: Export scale (1-4, default 2 for @2x)
            
        Returns:
            Image URL from Figma, or None if failed
        """
        # Request image export
        url = f"{self.BASE_URL}/images/{file_key}"
        params = {
            "ids": node_id,
            "format": "png",
            "scale": str(scale)
        }
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        
        # Get the export URL
        export_data = response.json()
        image_url = export_data.get("images", {}).get(node_id)
        
        return image_url
    
    def get_frame_by_name(self, file_key: str, frame_name: str, page_name: Optional[str] = None) -> Optional[str]:
        """
        Find a frame by name in a file and return its node ID.
        
        Args:
            file_key: The Figma file key
            frame_name: Name of the frame to find
            page_name: Optional page name to narrow search
            
        Returns:
            Node ID if found, None otherwise
        """
        file_data = self.get_file(file_key)
        
        def search_frames(node, target_name, current_page=None):
            # Check if this is the target frame
            node_type = node.get("type", "")
            node_name = node.get("name", "")
            
            if node_type == "FRAME" and target_name.lower() in node_name.lower():
                # If page filter specified, check if we're on the right page
                if page_name is None or (current_page and page_name.lower() in current_page.lower()):
                    return node.get("id")
            
            # Track current page
            if node_type == "CANVAS":
                current_page = node_name
            
            # Search children
            for child in node.get("children", []):
                result = search_frames(child, target_name, current_page)
                if result:
                    return result
            
            return None
        
        return search_frames(file_data.get("document", {}), frame_name)
    
    def search_node_by_name(self, file_key: str, node_name: str) -> Optional[str]:
        """
        Search for a node by name in a file and return its ID.
        Uses fuzzy matching to find nodes even with slight name variations.
        Prioritizes Component/Instance nodes over Text nodes.
        
        Args:
            file_key: The Figma file key
            node_name: Name to search for
            
        Returns:
            Node ID if found, None otherwise
        """
        file_data = self.get_file(file_key)
        target_lower = node_name.lower().strip()
        target_words = set(target_lower.split())
        
        best_match = None
        best_score = 0
        
        def search_recursive(node):
            nonlocal best_match, best_score
            
            node_name_str = node.get("name", "")
            node_name_lower = node_name_str.lower()
            node_type = node.get("type", "")
            
            # Calculate base score
            score = 0
            
            # Exact match (case-insensitive) - highest priority
            if node_name_lower == target_lower:
                score = 1000  # Much higher score for exact matches
            # Hyphenated exact match (e.g., "ice-cream-cone" matches "ice cream cone")
            elif node_name_lower.replace('-', ' ') == target_lower or target_lower.replace(' ', '-') == node_name_lower:
                score = 900
            # Contains match
            elif target_lower in node_name_lower or node_name_lower in target_lower:
                score = 50
                # Word overlap scoring
                node_words = set(node_name_lower.split())
                overlap = len(target_words & node_words)
                if overlap > 0:
                    score = 50 + (overlap * 10)
            
            # Type priority: INSTANCE > COMPONENT > FRAME > others > TEXT
            type_priority = {
                'INSTANCE': 1000,
                'COMPONENT': 800,
                'FRAME': 600,
                'GROUP': 400,
                'RECTANGLE': 200,
                'ELLIPSE': 200,
                'TEXT': 0  # Lowest priority for text nodes
            }
            
            type_bonus = type_priority.get(node_type, 100)
            total_score = score + type_bonus
            
            if score > 0 and total_score > best_score:
                best_score = total_score
                best_match = node.get("id")
            
            for child in node.get("children", []):
                search_recursive(child)
        
        search_recursive(file_data.get("document", {}))
        
        return best_match
    
    def change_svg_color(self, svg_content: str, new_color: str) -> str:
        """
        Change all fill colors in an SVG to a new color.
        
        Args:
            svg_content: SVG content as string
            new_color: New hex color (e.g., "#1B8751")
            
        Returns:
            Modified SVG content
        """
        import re
        
        # Replace all fill colors with the new color
        svg_content = re.sub(r'fill="[^"]*"', f'fill="{new_color}"', svg_content)
        
        return svg_content


# Global Figma client instance
figma_client = FigmaClient()


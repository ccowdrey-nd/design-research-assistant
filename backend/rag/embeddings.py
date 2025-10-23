"""
Vector embeddings and ChromaDB management.
"""
import chromadb
from chromadb.config import Settings as ChromaSettings
from openai import OpenAI
from typing import List, Dict, Any, Optional
from config import settings
import hashlib


class EmbeddingManager:
    """Manages vector embeddings and ChromaDB storage."""
    
    def __init__(self):
        self.client = OpenAI(api_key=settings.openai_api_key)
        
        # Initialize ChromaDB
        self.chroma_client = chromadb.PersistentClient(
            path=settings.chroma_persist_directory,
            settings=ChromaSettings(
                anonymized_telemetry=False,
            )
        )
        
        # Get or create collections
        self.design_collection = self.chroma_client.get_or_create_collection(
            name="design_system",
            metadata={"description": "Design system components, styles, and documentation"}
        )
    
    def create_embedding(self, text: str) -> List[float]:
        """
        Create an embedding for the given text using OpenAI.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector
        """
        response = self.client.embeddings.create(
            model=settings.embedding_model,
            input=text
        )
        return response.data[0].embedding
    
    def create_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Create embeddings for multiple texts in a batch.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        if not texts:
            return []
        
        response = self.client.embeddings.create(
            model=settings.embedding_model,
            input=texts
        )
        return [item.embedding for item in response.data]
    
    def add_documents(
        self,
        documents: List[str],
        metadatas: List[Dict[str, Any]],
        ids: Optional[List[str]] = None
    ) -> None:
        """
        Add documents to the vector store.
        
        Args:
            documents: List of text documents
            metadatas: List of metadata dictionaries
            ids: Optional list of document IDs (auto-generated if not provided)
        """
        if not documents:
            return
        
        # Generate IDs if not provided
        if ids is None:
            ids = [self._generate_id(doc, meta, idx) for idx, (doc, meta) in enumerate(zip(documents, metadatas))]
        
        # Create embeddings
        embeddings = self.create_embeddings_batch(documents)
        
        # Add to ChromaDB
        self.design_collection.add(
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids
        )
    
    def add_figma_components(self, components: List[Dict[str, Any]], file_key: str) -> None:
        """
        Add Figma components to the vector store.
        
        Args:
            components: List of component dictionaries
            file_key: Figma file key
        """
        documents = []
        metadatas = []
        
        for comp in components:
            # Create a rich text description
            doc_text = f"Component: {comp['name']}\n"
            if comp.get('description'):
                doc_text += f"Description: {comp['description']}\n"
            
            documents.append(doc_text)
            metadatas.append({
                "source": "figma",
                "type": "component",
                "name": comp['name'],
                "file_key": file_key,
                "component_id": comp['id'],
                "url": f"https://www.figma.com/file/{file_key}?node-id={comp['id']}"
            })
        
        self.add_documents(documents, metadatas)
    
    def add_figma_page_content(self, pages: List[Dict[str, Any]]) -> None:
        """
        Add Figma page content to the vector store.
        
        Args:
            pages: List of page content dictionaries
        """
        documents = []
        metadatas = []
        
        for page in pages:
            content = page['content']
            page_name = page['page_name']
            is_example = page.get('is_example', False)
            example_type = page.get('example_type')
            content_category = page.get('content_category', 'general')
            
            # Chunk large content to avoid embedding token limits
            max_chunk_size = 2000  # characters per chunk
            
            if len(content) > max_chunk_size:
                # Split into chunks
                chunks = []
                for i in range(0, len(content), max_chunk_size):
                    chunk = content[i:i+max_chunk_size]
                    chunks.append(chunk)
                
                # Add each chunk as a separate document
                for idx, chunk in enumerate(chunks):
                    doc_text = f"Page: {page_name} from {page['file_name']} (Part {idx+1}/{len(chunks)})\n\n{chunk}"
                    documents.append(doc_text)
                    metadatas.append({
                        "source": "figma",
                        "type": "page_content",
                        "name": f"{page_name} (Part {idx+1})",
                        "file_key": page['file_key'],
                        "file_name": page['file_name'],
                        "url": f"https://www.figma.com/file/{page['file_key']}",
                        "is_example": str(is_example),
                        "example_type": example_type or "",
                        "content_category": content_category
                    })
            else:
                # Add whole page as single document
                doc_text = f"Page: {page_name} from {page['file_name']}\n\n{content}"
                documents.append(doc_text)
                metadatas.append({
                    "source": "figma",
                    "type": "page_content",
                    "name": page_name,
                    "file_key": page['file_key'],
                    "file_name": page['file_name'],
                    "url": f"https://www.figma.com/file/{page['file_key']}",
                    "is_example": str(is_example),
                    "example_type": example_type or "",
                    "content_category": content_category
                })
        
        if documents:
            # Add in batches to avoid overwhelming the API
            batch_size = 20
            for i in range(0, len(documents), batch_size):
                batch_docs = documents[i:i+batch_size]
                batch_metas = metadatas[i:i+batch_size]
                self.add_documents(batch_docs, batch_metas)
    
    def add_figma_styles(self, tokens: Dict[str, Any]) -> None:
        """
        Add Figma design tokens/styles to the vector store.
        
        Args:
            tokens: Design tokens dictionary
        """
        documents = []
        metadatas = []
        file_key = tokens.get('file_key', '')
        
        # Add color styles
        for color in tokens.get('colors', []):
            doc_text = f"Color Style: {color['name']}\n"
            if color.get('description'):
                doc_text += f"Description: {color['description']}\n"
            
            documents.append(doc_text)
            metadatas.append({
                "source": "figma",
                "type": "color",
                "name": color['name'],
                "file_key": file_key,
                "style_id": color['id'],
                "url": f"https://www.figma.com/file/{file_key}"
            })
        
        # Add typography styles
        for typo in tokens.get('typography', []):
            doc_text = f"Typography Style: {typo['name']}\n"
            if typo.get('description'):
                doc_text += f"Description: {typo['description']}\n"
            
            documents.append(doc_text)
            metadatas.append({
                "source": "figma",
                "type": "typography",
                "name": typo['name'],
                "file_key": file_key,
                "style_id": typo['id'],
                "url": f"https://www.figma.com/file/{file_key}"
            })
        
        if documents:
            self.add_documents(documents, metadatas)
    
    def add_figma_file_metadata(self, files: List[Dict[str, Any]]) -> None:
        """
        Add Figma file metadata to the vector store for searchability.
        
        Args:
            files: List of file metadata dictionaries
        """
        documents = []
        metadatas = []
        
        for file in files:
            # Create searchable document from file metadata
            doc_text = f"Figma File: {file['name']}\n"
            doc_text += f"Project: {file['project']}\n"
            doc_text += f"Last modified: {file.get('last_modified', 'Unknown')}\n"
            doc_text += f"URL: {file['url']}\n"
            
            documents.append(doc_text)
            metadatas.append({
                "source": "figma",
                "type": "file_metadata",
                "name": file['name'],
                "file_key": file['key'],
                "project": file['project'],
                "url": file['url'],
                "last_modified": file.get('last_modified', '')
            })
        
        if documents:
            self.add_documents(documents, metadatas)
    
    def add_slides_content(self, presentation: Dict[str, Any]) -> None:
        """
        Add Google Slides content to the vector store.
        
        Args:
            presentation: Presentation content dictionary
        """
        documents = []
        metadatas = []
        
        pres_id = presentation.get('presentation_id', '')
        pres_name = presentation.get('name', 'Untitled')
        web_link = presentation.get('web_view_link', '')
        
        for slide in presentation.get('slides', []):
            # Combine slide text
            all_text = ' '.join(slide.get('texts', []))
            speaker_notes = slide.get('speaker_notes', '')
            
            doc_text = f"Slide {slide['slide_number']} from '{pres_name}'\n"
            if all_text:
                doc_text += f"Content: {all_text}\n"
            if speaker_notes:
                doc_text += f"Notes: {speaker_notes}\n"
            
            if all_text or speaker_notes:
                documents.append(doc_text)
                metadatas.append({
                    "source": "google_slides",
                    "type": "slide",
                    "presentation_name": pres_name,
                    "presentation_id": pres_id,
                    "slide_number": slide['slide_number'],
                    "url": web_link
                })
        
        if documents:
            self.add_documents(documents, metadatas)
    
    def clear_collection(self) -> None:
        """Clear all documents from the collection."""
        self.chroma_client.delete_collection(name="design_system")
        self.design_collection = self.chroma_client.get_or_create_collection(
            name="design_system",
            metadata={"description": "Design system components, styles, and documentation"}
        )
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the collection."""
        count = self.design_collection.count()
        return {
            "total_documents": count,
            "collection_name": "design_system"
        }
    
    def _generate_id(self, document: str, metadata: Dict[str, Any], index: int = 0) -> str:
        """Generate a unique ID for a document."""
        # Include more metadata to ensure uniqueness across files
        unique_parts = [
            str(index),  # Add index to ensure uniqueness
            metadata.get('source', ''),
            metadata.get('type', ''),
            metadata.get('file_key', ''),
            metadata.get('presentation_id', ''),
            metadata.get('name', ''),
            str(metadata.get('slide_number', '')),
            document[:200]
        ]
        content = "_".join(str(p) for p in unique_parts if p)
        return hashlib.md5(content.encode()).hexdigest()


# Global embedding manager instance
embedding_manager = EmbeddingManager()


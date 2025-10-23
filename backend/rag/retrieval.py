"""
Document retrieval and context management for RAG.
"""
from typing import List, Dict, Any, Optional
from rag.embeddings import embedding_manager
from config import settings


class RetrievalManager:
    """Manages document retrieval for RAG pipeline."""
    
    def __init__(self):
        self.embedding_manager = embedding_manager
        self.collection = embedding_manager.design_collection
    
    def search(
        self,
        query: str,
        top_k: Optional[int] = None,
        filter_dict: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Search for relevant documents using semantic similarity.
        
        Args:
            query: Search query text
            top_k: Number of results to return (default from settings)
            filter_dict: Optional metadata filters
            
        Returns:
            Search results with documents and metadata
        """
        top_k = top_k or settings.top_k_results
        
        # Create query embedding
        query_embedding = self.embedding_manager.create_embedding(query)
        
        # Search in ChromaDB
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=filter_dict
        )
        
        return self._format_results(results)
    
    def search_by_source(
        self,
        query: str,
        source: str,
        top_k: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Search within a specific source (figma, google_slides).
        
        Args:
            query: Search query text
            source: Source type to filter by
            top_k: Number of results to return
            
        Returns:
            Filtered search results
        """
        return self.search(
            query=query,
            top_k=top_k,
            filter_dict={"source": source}
        )
    
    def search_by_type(
        self,
        query: str,
        doc_type: str,
        top_k: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Search for a specific document type (component, color, typography, slide).
        
        Args:
            query: Search query text
            doc_type: Document type to filter by
            top_k: Number of results to return
            
        Returns:
            Filtered search results
        """
        return self.search(
            query=query,
            top_k=top_k,
            filter_dict={"type": doc_type}
        )
    
    def build_context(
        self,
        query: str,
        max_context_length: int = 3000
    ) -> str:
        """
        Build context string for LLM from retrieved documents.
        
        Args:
            query: User query
            max_context_length: Maximum character length for context
            
        Returns:
            Formatted context string
        """
        results = self.search(query)
        
        context_parts = ["Relevant information from the design system:\n"]
        current_length = len(context_parts[0])
        
        for doc, metadata in zip(results['documents'], results['metadatas']):
            # Format the document with its source
            source_info = self._format_source_info(metadata)
            doc_text = f"\n{source_info}\n{doc}\n"
            
            # Check if adding this document would exceed the limit
            if current_length + len(doc_text) > max_context_length:
                break
            
            context_parts.append(doc_text)
            current_length += len(doc_text)
        
        return "".join(context_parts)
    
    def get_sources(self, query: str) -> List[Dict[str, Any]]:
        """
        Get source citations for a query.
        
        Args:
            query: User query
            
        Returns:
            List of source citations with URLs
        """
        results = self.search(query)
        sources = []
        
        for metadata in results['metadatas']:
            source = {
                "name": metadata.get('name', 'Unnamed'),
                "source": metadata.get('source', ''),
                "type": metadata.get('type', ''),
                "url": metadata.get('url', '')
            }
            sources.append(source)
        
        return sources
    
    def _format_results(self, raw_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format ChromaDB results into a cleaner structure.
        
        Args:
            raw_results: Raw results from ChromaDB
            
        Returns:
            Formatted results
        """
        if not raw_results.get('documents') or not raw_results['documents'][0]:
            return {
                'documents': [],
                'metadatas': [],
                'distances': []
            }
        
        return {
            'documents': raw_results['documents'][0],
            'metadatas': raw_results['metadatas'][0],
            'distances': raw_results.get('distances', [[]])[0]
        }
    
    def search_examples(self, example_type: str, top_k: int = 5) -> Dict[str, Any]:
        """
        Search for example designs by type (email or ad).
        
        Args:
            example_type: Type of example to search for ("email" or "ad")
            top_k: Number of examples to return
            
        Returns:
            Search results with example designs
        """
        # Search for examples with specific type
        query = f"{example_type} design template example"
        
        results = self.collection.query(
            query_embeddings=[self.embedding_manager.create_embedding(query)],
            n_results=top_k * 2,  # Get more to filter
        )
        
        formatted = self._format_results(results)
        
        # Filter for actual examples
        filtered_docs = []
        filtered_metas = []
        
        for doc, meta in zip(formatted['documents'], formatted['metadatas']):
            if (meta.get('is_example') == 'True' and 
                meta.get('example_type') == example_type):
                filtered_docs.append(doc)
                filtered_metas.append(meta)
                if len(filtered_docs) >= top_k:
                    break
        
        return {
            'documents': filtered_docs,
            'metadatas': filtered_metas
        }
    
    def _format_source_info(self, metadata: Dict[str, Any]) -> str:
        """
        Format metadata into a readable source citation.
        
        Args:
            metadata: Document metadata
            
        Returns:
            Formatted source string
        """
        source = metadata.get('source', 'unknown')
        doc_type = metadata.get('type', '')
        name = metadata.get('name', '')
        
        if source == 'figma':
            return f"[Figma {doc_type.title()}: {name}]"
        elif source == 'google_slides':
            pres_name = metadata.get('presentation_name', '')
            slide_num = metadata.get('slide_number', '')
            return f"[Google Slides - {pres_name}, Slide {slide_num}]"
        else:
            return f"[{source}: {name}]"


# Global retrieval manager instance
retrieval_manager = RetrievalManager()


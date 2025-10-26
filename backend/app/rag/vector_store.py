"""Vector database management using ChromaDB."""
import chromadb
from typing import List, Dict, Any, Optional
import logging
from sentence_transformers import SentenceTransformer

from app.config import settings

logger = logging.getLogger(__name__)


class VectorStore:
    """Manages vector storage and retrieval using ChromaDB."""
    
    def __init__(self):
        """Initialize ChromaDB client and embedding model."""
        self.client = chromadb.PersistentClient(
            path=settings.CHROMA_PERSIST_DIRECTORY
        )
        self.embedding_model = SentenceTransformer(settings.EMBEDDING_MODEL)
        self.collection = self._get_or_create_collection()
        logger.info("VectorStore initialized successfully")
    
    def _get_or_create_collection(self):
        """Get or create the main collection."""
        try:
            collection = self.client.get_collection("documents")
            logger.info("Retrieved existing collection")
        except Exception:
            collection = self.client.create_collection(
                name="documents",
                metadata={"hnsw:space": "cosine"}
            )
            logger.info("Created new collection")
        return collection
    
    def add_documents(
        self,
        texts: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None
    ) -> None:
        """Add documents to the vector store.
        
        Args:
            texts: List of document texts to add
            metadatas: Optional metadata for each document
            ids: Optional IDs for each document
        """
        try:
            embeddings = self.embedding_model.encode(texts).tolist()
            
            if ids is None:
                import uuid
                ids = [str(uuid.uuid4()) for _ in texts]
            
            if metadatas is None:
                metadatas = [{} for _ in texts]
            
            self.collection.add(
                embeddings=embeddings,
                documents=texts,
                metadatas=metadatas,
                ids=ids
            )
            logger.info(f"Added {len(texts)} documents to vector store")
        except Exception as e:
            logger.error(f"Error adding documents: {e}")
            raise
    
    def search(
        self,
        query: str,
        n_results: int = None
    ) -> List[Dict[str, Any]]:
        """Search for similar documents.
        
        Args:
            query: Search query
            n_results: Number of results to return
            
        Returns:
            List of matching documents with metadata
        """
        try:
            if n_results is None:
                n_results = settings.TOP_K_RESULTS
            
            query_embedding = self.embedding_model.encode([query]).tolist()
            
            results = self.collection.query(
                query_embeddings=query_embedding,
                n_results=n_results
            )
            
            # Format results
            formatted_results = []
            if results['documents'] and results['documents'][0]:
                for i, doc in enumerate(results['documents'][0]):
                    formatted_results.append({
                        'text': doc,
                        'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                        'distance': results['distances'][0][i] if results['distances'] else 0,
                        'id': results['ids'][0][i]
                    })
            
            logger.info(f"Found {len(formatted_results)} results for query")
            return formatted_results
        except Exception as e:
            logger.error(f"Error searching documents: {e}")
            raise
    
    def delete_documents(self, ids: List[str]) -> None:
        """Delete documents by IDs."""
        try:
            self.collection.delete(ids=ids)
            logger.info(f"Deleted {len(ids)} documents")
        except Exception as e:
            logger.error(f"Error deleting documents: {e}")
            raise
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the collection."""
        try:
            count = self.collection.count()
            return {
                'total_documents': count,
                'collection_name': self.collection.name
            }
        except Exception as e:
            logger.error(f"Error getting collection stats: {e}")
            return {'total_documents': 0, 'collection_name': 'documents'}


# Global instance
vector_store = VectorStore()

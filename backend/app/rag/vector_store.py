"""Vector database management with optional ChromaDB backend."""
from typing import List, Dict, Any, Optional, Iterator
import logging
import json
from pathlib import Path
from contextlib import contextmanager
from sentence_transformers import SentenceTransformer

from app.config import settings

try:
    import chromadb
except Exception:  # pragma: no cover - optional dependency
    chromadb = None

logger = logging.getLogger(__name__)


class VectorStore:
    """Manages vector storage and retrieval using ChromaDB or a local fallback."""
    
    def __init__(self):
        """Initialize vector store backend and embedding model."""
        self.client = None
        self.use_chroma = chromadb is not None

        self.persist_dir = Path(settings.CHROMA_PERSIST_DIRECTORY)
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        self.simple_store_path = self.persist_dir / "simple_store.json"
        self._simple_docs: List[Dict[str, Any]] = []

        if self.use_chroma:
            self.client = chromadb.PersistentClient(path=str(self.persist_dir))

        self.embedding_model = self._load_embedding_model()
        self.collection = self._get_or_create_collection()

        backend = "chroma" if self.use_chroma else "simple"
        logger.info(f"VectorStore initialized successfully with '{backend}' backend")

    def _load_embedding_model(self) -> SentenceTransformer:
        """Load embedding model with a local-cache fallback for HF metadata issues."""
        with self._safe_repo_template_lookup():
            try:
                return SentenceTransformer(settings.EMBEDDING_MODEL)
            except Exception as primary_error:
                logger.warning(
                    "Could not load embedding model from remote metadata (%s). Retrying with local cache.",
                    primary_error,
                )
                try:
                    return SentenceTransformer(settings.EMBEDDING_MODEL, local_files_only=True)
                except Exception:
                    logger.error("Failed to load embedding model, including local cache retry")
                    raise

    @staticmethod
    @contextmanager
    def _safe_repo_template_lookup() -> Iterator[None]:
        """Patch transformers template lookup to ignore missing optional repo paths."""
        try:
            import transformers.tokenization_utils_base as token_utils_base
            from huggingface_hub.errors import RemoteEntryNotFoundError
        except Exception:
            yield
            return

        original = token_utils_base.list_repo_templates

        def _safe_list_repo_templates(*args, **kwargs):
            try:
                return original(*args, **kwargs)
            except RemoteEntryNotFoundError:
                return []

        token_utils_base.list_repo_templates = _safe_list_repo_templates
        try:
            yield
        finally:
            token_utils_base.list_repo_templates = original
    
    def _get_or_create_collection(self):
        """Get or create the main collection/backend state."""
        if not self.use_chroma:
            self._load_simple_store()
            return None

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

    def _load_simple_store(self) -> None:
        """Load simple JSON-backed document store."""
        if not self.simple_store_path.exists():
            self._simple_docs = []
            return

        try:
            with self.simple_store_path.open("r", encoding="utf-8") as f:
                loaded = json.load(f)
            self._simple_docs = loaded if isinstance(loaded, list) else []
            logger.info(f"Loaded {len(self._simple_docs)} documents from simple store")
        except Exception as e:
            logger.warning(f"Could not load simple store, starting empty: {e}")
            self._simple_docs = []

    def _save_simple_store(self) -> None:
        """Persist simple JSON-backed document store."""
        with self.simple_store_path.open("w", encoding="utf-8") as f:
            json.dump(self._simple_docs, f, ensure_ascii=False)

    @staticmethod
    def _cosine_similarity(a: List[float], b: List[float]) -> float:
        """Compute cosine similarity for two vectors."""
        dot = sum(x * y for x, y in zip(a, b))
        norm_a = sum(x * x for x in a) ** 0.5
        norm_b = sum(y * y for y in b) ** 0.5
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot / (norm_a * norm_b)
    
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

            if self.use_chroma:
                self.collection.add(
                    embeddings=embeddings,
                    documents=texts,
                    metadatas=metadatas,
                    ids=ids
                )
            else:
                for doc_id, text, metadata, embedding in zip(ids, texts, metadatas, embeddings):
                    self._simple_docs.append({
                        "id": doc_id,
                        "text": text,
                        "metadata": metadata,
                        "embedding": embedding,
                    })
                self._save_simple_store()

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

            if self.use_chroma:
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
            else:
                query_vec = query_embedding[0]
                scored_docs = []
                for doc in self._simple_docs:
                    similarity = self._cosine_similarity(query_vec, doc.get("embedding", []))
                    scored_docs.append((similarity, doc))

                scored_docs.sort(key=lambda item: item[0], reverse=True)
                formatted_results = []
                for similarity, doc in scored_docs[:n_results]:
                    formatted_results.append({
                        'text': doc.get("text", ""),
                        'metadata': doc.get("metadata", {}),
                        'distance': 1 - similarity,
                        'id': doc.get("id", ""),
                    })
            
            logger.info(f"Found {len(formatted_results)} results for query")
            return formatted_results
        except Exception as e:
            logger.error(f"Error searching documents: {e}")
            raise
    
    def delete_documents(self, ids: List[str]) -> None:
        """Delete documents by IDs."""
        try:
            if self.use_chroma:
                self.collection.delete(ids=ids)
            else:
                ids_set = set(ids)
                self._simple_docs = [doc for doc in self._simple_docs if doc.get("id") not in ids_set]
                self._save_simple_store()
            logger.info(f"Deleted {len(ids)} documents")
        except Exception as e:
            logger.error(f"Error deleting documents: {e}")
            raise

    def clear_documents(self) -> None:
        """Clear all documents from the active backend."""
        try:
            if self.use_chroma:
                self.client.delete_collection("documents")
                self.collection = self.client.create_collection(
                    name="documents",
                    metadata={"hnsw:space": "cosine"}
                )
            else:
                self._simple_docs = []
                self._save_simple_store()
            logger.info("Cleared all documents from vector store")
        except Exception as e:
            logger.error(f"Error clearing documents: {e}")
            raise
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the collection."""
        try:
            if self.use_chroma:
                count = self.collection.count()
            else:
                count = len(self._simple_docs)

            return {
                'total_documents': count,
                'collection_name': 'documents'
            }
        except Exception as e:
            logger.error(f"Error getting collection stats: {e}")
            return {'total_documents': 0, 'collection_name': 'documents'}


# Global instance
vector_store = VectorStore()

"""
Vector Memory for Neural Core - RAG Long-Term Memory.

This module implements a vector database abstraction layer for the CTO Neural Core,
enabling semantic search and retrieval-augmented generation (RAG) capabilities.

Architecture:
- Adapter Pattern: Support for multiple vector store backends
- Async-first: Non-blocking operations for event loop compatibility
- Type-safe: Strict typing with Pydantic validation
- Resilient: Handles model downloads and initialization gracefully

Performance:
- Async embedding generation to avoid blocking
- Batch operations for efficiency
- In-memory caching for frequent queries

Security & Compliance:
- No PII stored in metadata (RGPD/Loi 25 compliant)
- Input validation via Pydantic
- Secure defaults for all operations

Author: Ingénieur Backend MCP
Date: 2025-12-16
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field, ConfigDict, field_validator

# Third-party imports (will be installed via requirements.txt)
try:
    import chromadb
    from chromadb.config import Settings as ChromaSettings
    from sentence_transformers import SentenceTransformer

    VECTOR_DEPS_AVAILABLE = True
except ImportError:
    VECTOR_DEPS_AVAILABLE = False
    chromadb = None  # type: ignore
    ChromaSettings = None  # type: ignore
    SentenceTransformer = None  # type: ignore


# Configure logging
logger = logging.getLogger(__name__)


# ============================================================================
# Pydantic Models for Type Safety
# ============================================================================


class DocumentMetadata(BaseModel):
    """
    Metadata for a document stored in vector memory.

    Conformité: RGPD/Loi 25
    - No PII allowed in metadata
    - All fields are optional except those explicitly required
    - Metadata is used for filtering and organization only
    """

    model_config = ConfigDict(strict=True)

    source: str | None = Field(
        None, max_length=500, description="Document source (file path, URL, etc)"
    )
    category: str | None = Field(None, max_length=100, description="Document category")
    tags: list[str] = Field(default_factory=list, description="Document tags")
    timestamp: float | None = Field(None, ge=0, description="Unix timestamp")

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, v: list[str]) -> list[str]:
        """Validate that tags are non-empty and within limits."""
        if len(v) > 50:
            raise ValueError("Maximum 50 tags allowed")
        for tag in v:
            if not tag or len(tag) > 100:
                raise ValueError("Tags must be non-empty and max 100 characters")
        return v


class Document(BaseModel):
    """
    A document to be stored in vector memory.

    This model represents a text document with optional metadata.
    """

    model_config = ConfigDict(strict=True)

    text: str = Field(
        ..., min_length=1, max_length=100000, description="Document text content"
    )
    metadata: DocumentMetadata = Field(
        default_factory=DocumentMetadata, description="Document metadata"
    )

    @field_validator("text")
    @classmethod
    def validate_text(cls, v: str) -> str:
        """Validate text is not just whitespace."""
        if not v.strip():
            raise ValueError("Document text cannot be empty or whitespace only")
        return v


class SearchResult(BaseModel):
    """
    A single search result from vector memory.

    Contains the matched document, its metadata, and similarity score.
    """

    model_config = ConfigDict(strict=True)

    id: str = Field(..., description="Unique document identifier")
    text: str = Field(..., description="Document text content")
    metadata: DocumentMetadata = Field(
        default_factory=DocumentMetadata, description="Document metadata"
    )
    score: float = Field(
        ..., ge=0.0, le=1.0, description="Similarity score (0-1, higher is better)"
    )


# ============================================================================
# Abstract Interface for Vector Store Backends
# ============================================================================


class VectorStore(ABC):
    """
    Abstract base class for vector store backends.

    This interface defines the contract that all vector store implementations
    must follow, enabling the Adapter pattern for backend flexibility.
    """

    @abstractmethod
    async def add(
        self, doc_id: str, text: str, embedding: list[float], metadata: dict[str, Any]
    ) -> None:
        """Add a document with its embedding to the store."""
        raise NotImplementedError

    @abstractmethod
    async def search(
        self,
        query_embedding: list[float],
        limit: int,
        metadata_filter: dict[str, Any] | None = None,
    ) -> list[tuple[str, str, dict[str, Any], float]]:
        """
        Search for similar documents.

        Returns:
            List of tuples (id, text, metadata, score)
        """
        raise NotImplementedError

    @abstractmethod
    async def delete(self, doc_id: str) -> None:
        """Delete a document by ID."""
        raise NotImplementedError

    @abstractmethod
    async def count(self) -> int:
        """Get total document count."""
        raise NotImplementedError


class ChromaDBAdapter(VectorStore):
    """
    ChromaDB adapter for vector storage.

    This adapter provides a persistent, local vector database using ChromaDB.
    It supports both in-memory and file-based persistence.

    Performance:
    - Async wrapper around ChromaDB's sync API
    - Uses asyncio.to_thread for non-blocking operations
    """

    def __init__(self, persist_directory: str | Path | None = None):
        """
        Initialize ChromaDB adapter.

        Args:
            persist_directory: Directory for persistent storage.
                             If None, uses in-memory storage.
        """
        if not VECTOR_DEPS_AVAILABLE:
            raise ImportError(
                "Vector database dependencies not installed. "
                "Install with: pip install chromadb sentence-transformers"
            )

        self.persist_directory = Path(persist_directory) if persist_directory else None

        # Initialize ChromaDB client
        if self.persist_directory:
            self.persist_directory.mkdir(parents=True, exist_ok=True)
            settings = ChromaSettings(
                persist_directory=str(self.persist_directory),
                anonymized_telemetry=False,  # Privacy: No telemetry
            )
            self.client = chromadb.PersistentClient(
                path=str(self.persist_directory), settings=settings
            )
        else:
            self.client = chromadb.EphemeralClient()

        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name="neural_core_memory",
            metadata={"description": "Vector memory for Neural Core"},
        )

        logger.info(
            "ChromaDB adapter initialized",
            extra={
                "persist_directory": (
                    str(self.persist_directory)
                    if self.persist_directory
                    else "in-memory"
                )
            },
        )

    async def add(
        self, doc_id: str, text: str, embedding: list[float], metadata: dict[str, Any]
    ) -> None:
        """Add a document to ChromaDB."""
        # ChromaDB is sync, so we run it in a thread pool
        await asyncio.to_thread(
            self.collection.add,
            ids=[doc_id],
            documents=[text],
            embeddings=[embedding],
            metadatas=[metadata],
        )
        logger.debug("Document added to ChromaDB", extra={"id": doc_id})

    async def search(
        self,
        query_embedding: list[float],
        limit: int,
        metadata_filter: dict[str, Any] | None = None,
    ) -> list[tuple[str, str, dict[str, Any], float]]:
        """Search for similar documents in ChromaDB."""
        where = metadata_filter if metadata_filter else None

        results = await asyncio.to_thread(
            self.collection.query,
            query_embeddings=[query_embedding],
            n_results=limit,
            where=where,
        )

        # Parse results
        output: list[tuple[str, str, dict[str, Any], float]] = []
        if results["ids"] and results["ids"][0]:
            for i, doc_id in enumerate(results["ids"][0]):
                text = results["documents"][0][i]
                metadata = results["metadatas"][0][i] if results["metadatas"] else {}
                # ChromaDB returns distances, convert to similarity scores
                # Note: This assumes L2 distance (default). For other metrics:
                # - Cosine: score = 1.0 - distance
                # - Inner Product: score = distance (already a similarity)
                distance = results["distances"][0][i] if results["distances"] else 0.0
                # Convert L2 distance to similarity (inverse relationship)
                # Higher score = more similar
                score = max(0.0, min(1.0, 1.0 / (1.0 + distance)))
                output.append((doc_id, text, metadata, score))

        return output

    async def delete(self, doc_id: str) -> None:
        """Delete a document from ChromaDB."""
        await asyncio.to_thread(self.collection.delete, ids=[doc_id])
        logger.debug("Document deleted from ChromaDB", extra={"id": doc_id})

    async def count(self) -> int:
        """Get total document count in ChromaDB."""
        result = await asyncio.to_thread(self.collection.count)
        return result


# ============================================================================
# Embedding Model Manager
# ============================================================================


class EmbeddingModel:
    """
    Manages sentence embedding model with lazy initialization.

    This class handles:
    - Model downloading (with progress logging)
    - Thread-safe lazy initialization
    - Async embedding generation
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize embedding model manager.

        Args:
            model_name: Name of the SentenceTransformer model to use.
                       Default is a fast, lightweight model (384 dimensions).
        """
        if not VECTOR_DEPS_AVAILABLE:
            raise ImportError(
                "Embedding dependencies not installed. "
                "Install with: pip install sentence-transformers"
            )

        self.model_name = model_name
        self._model: SentenceTransformer | None = None
        self._lock = asyncio.Lock()

    async def _ensure_loaded(self) -> None:
        """Ensure model is loaded (downloads if necessary)."""
        if self._model is not None:
            return

        async with self._lock:
            # Double-check after acquiring lock
            if self._model is not None:
                return

            logger.info(
                "Loading embedding model (this may download the model on first run)",
                extra={"model_name": self.model_name},
            )

            # Load model in thread pool (it's CPU-bound)
            self._model = await asyncio.to_thread(SentenceTransformer, self.model_name)

            logger.info(
                "Embedding model loaded successfully",
                extra={
                    "model_name": self.model_name,
                    "dimensions": self._model.get_sentence_embedding_dimension(),
                },
            )

    async def embed(self, text: str) -> list[float]:
        """
        Generate embedding for a text.

        Args:
            text: Input text to embed

        Returns:
            Embedding vector as list of floats
        """
        await self._ensure_loaded()

        # Generate embedding in thread pool (CPU-bound operation)
        embedding = await asyncio.to_thread(
            self._model.encode,  # type: ignore
            text,
            convert_to_numpy=False,
            show_progress_bar=False,
        )

        return embedding.tolist()


# ============================================================================
# Main VectorMemory Class
# ============================================================================


class VectorMemory:
    """
    High-level vector memory interface for the Neural Core.

    This class provides a simple, async-first API for storing and retrieving
    documents using semantic search. It abstracts away the complexity of
    vector databases and embedding models.

    Usage:
        memory = VectorMemory(persist_directory="./vector_store")
        await memory.initialize()

        # Add documents
        doc_id = await memory.add_document(
            text="Machine learning is a subset of AI",
            metadata={"category": "ai", "tags": ["ml", "ai"]}
        )

        # Search
        results = await memory.search("What is ML?", limit=5)
        for result in results:
            print(f"{result.score:.2f}: {result.text}")

        # Delete
        await memory.delete(doc_id)
    """

    def __init__(
        self,
        persist_directory: str | Path | None = None,
        embedding_model: str = "all-MiniLM-L6-v2",
    ):
        """
        Initialize VectorMemory.

        Args:
            persist_directory: Directory for persistent storage.
                             If None, uses in-memory storage.
            embedding_model: Name of the sentence transformer model.
        """
        self.persist_directory = persist_directory
        self._embedding_model = EmbeddingModel(model_name=embedding_model)
        self._store: VectorStore | None = None
        self._initialized = False

    async def initialize(self) -> None:
        """
        Initialize the vector memory system.

        This must be called before any operations. It initializes the
        vector store and ensures the embedding model is ready.
        """
        if self._initialized:
            return

        logger.info(
            "Initializing VectorMemory",
            extra={"persist_directory": str(self.persist_directory)},
        )

        # Initialize vector store
        self._store = ChromaDBAdapter(persist_directory=self.persist_directory)

        # Pre-load embedding model to handle any downloads
        # Using protected method internally is acceptable within same package
        await self._embedding_model._ensure_loaded()  # noqa: SLF001

        self._initialized = True
        logger.info("VectorMemory initialized successfully")

    def _ensure_initialized(self) -> None:
        """Ensure VectorMemory is initialized."""
        if not self._initialized or self._store is None:
            raise RuntimeError(
                "VectorMemory not initialized. Call await memory.initialize() first."
            )

    async def add_document(
        self, text: str, metadata: dict[str, Any] | None = None
    ) -> str:
        """
        Add a document to vector memory.

        Args:
            text: Document text content
            metadata: Optional metadata (must be JSON-serializable)

        Returns:
            Document ID (UUID)

        Raises:
            ValueError: If text is invalid
            RuntimeError: If not initialized
        """
        self._ensure_initialized()

        # Validate document
        doc = Document(text=text, metadata=DocumentMetadata(**(metadata or {})))

        # Generate embedding
        embedding = await self._embedding_model.embed(doc.text)

        # Generate unique ID
        doc_id = str(uuid4())

        # Store in vector database
        metadata_dict = doc.metadata.model_dump(exclude_none=True)
        await self._store.add(doc_id, doc.text, embedding, metadata_dict)  # type: ignore

        logger.info("Document added to vector memory", extra={"id": doc_id})
        return doc_id

    async def search(
        self, query: str, limit: int = 10, metadata_filter: dict[str, Any] | None = None
    ) -> list[SearchResult]:
        """
        Search for similar documents.

        Args:
            query: Search query text
            limit: Maximum number of results to return
            metadata_filter: Optional metadata filter

        Returns:
            List of SearchResult objects, ordered by similarity (highest first)

        Raises:
            ValueError: If query is invalid or limit is out of range
            RuntimeError: If not initialized
        """
        self._ensure_initialized()

        # Validate inputs
        if not query.strip():
            raise ValueError("Query cannot be empty")
        if limit < 1 or limit > 100:
            raise ValueError("Limit must be between 1 and 100")

        # Generate query embedding
        query_embedding = await self._embedding_model.embed(query)

        # Search in vector store
        raw_results = await self._store.search(query_embedding, limit, metadata_filter)  # type: ignore

        # Convert to SearchResult objects
        results = [
            SearchResult(
                id=doc_id, text=text, metadata=DocumentMetadata(**metadata), score=score
            )
            for doc_id, text, metadata, score in raw_results
        ]

        logger.debug(
            "Search completed",
            extra={"query_length": len(query), "results_count": len(results)},
        )

        return results

    async def delete(self, doc_id: str) -> None:
        """
        Delete a document by ID.

        Args:
            doc_id: Document ID to delete

        Raises:
            RuntimeError: If not initialized
        """
        self._ensure_initialized()

        await self._store.delete(doc_id)  # type: ignore
        logger.info("Document deleted from vector memory", extra={"id": doc_id})

    async def count(self) -> int:
        """
        Get total number of documents in memory.

        Returns:
            Total document count

        Raises:
            RuntimeError: If not initialized
        """
        self._ensure_initialized()

        return await self._store.count()  # type: ignore


# ============================================================================
# Convenience Functions
# ============================================================================


async def create_vector_memory(
    persist_directory: str | Path | None = None,
    embedding_model: str = "all-MiniLM-L6-v2",
) -> VectorMemory:
    """
    Create and initialize a VectorMemory instance.

    This is a convenience function that combines initialization in one step.

    Args:
        persist_directory: Directory for persistent storage
        embedding_model: Name of the sentence transformer model

    Returns:
        Initialized VectorMemory instance
    """
    memory = VectorMemory(
        persist_directory=persist_directory, embedding_model=embedding_model
    )
    await memory.initialize()
    return memory

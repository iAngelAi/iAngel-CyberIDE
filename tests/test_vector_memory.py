"""
Unit tests for VectorMemory system.

These tests validate:
1. Document addition with embeddings
2. Semantic search functionality
3. Document deletion
4. Metadata handling and filtering
5. Error handling and validation
6. Async operations and thread safety

Test Coverage:
- Basic CRUD operations
- Search with various queries
- Metadata validation
- Edge cases (empty queries, invalid limits, etc.)
- Initialization and lifecycle
- Model downloading and caching

Author: Ingénieur Backend MCP
Date: 2025-12-16
"""

import asyncio
import pytest
import pytest_asyncio
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
from pydantic import ValidationError

from backend.cto.memory import (
    VectorMemory,
    Document,
    DocumentMetadata,
    SearchResult,
    create_vector_memory,
)


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def vector_storage(tmp_path):
    """Create a temporary directory for vector storage."""
    storage = tmp_path / "vector_store"
    storage.mkdir()
    return storage


@pytest_asyncio.fixture
async def vector_memory(tmp_path):
    """Create and initialize a VectorMemory instance."""
    storage = tmp_path / "test_vectors"

    # Mock the dependencies to avoid actual downloads in tests
    with patch("backend.cto.memory.vectors.VECTOR_DEPS_AVAILABLE", True):
        with patch("backend.cto.memory.vectors.ChromaDBAdapter") as mock_adapter:
            with patch("backend.cto.memory.vectors.EmbeddingModel") as mock_embedding:
                # Setup mock embedding model
                mock_embed_instance = AsyncMock()
                mock_embed_instance.embed = AsyncMock(return_value=[0.1] * 384)
                mock_embed_instance._ensure_loaded = AsyncMock()
                mock_embedding.return_value = mock_embed_instance

                # Setup mock vector store
                mock_store_instance = AsyncMock()
                mock_store_instance.add = AsyncMock()
                mock_store_instance.search = AsyncMock(return_value=[])
                mock_store_instance.delete = AsyncMock()
                mock_store_instance.count = AsyncMock(return_value=0)
                mock_adapter.return_value = mock_store_instance

                # Now create VectorMemory with mocks in place
                memory = VectorMemory(persist_directory=storage)

                # Override the private attributes
                memory._embedding_model = mock_embed_instance
                memory._store = mock_store_instance

                await memory.initialize()
                yield memory


# ============================================================================
# Test: Pydantic Models
# ============================================================================


def test_document_metadata_validation():
    """Test DocumentMetadata validation."""
    # Valid metadata
    metadata = DocumentMetadata(
        source="test.txt", category="test", tags=["tag1", "tag2"]
    )
    assert metadata.source == "test.txt"
    assert metadata.category == "test"
    assert len(metadata.tags) == 2

    # Test with no tags (should use default empty list)
    metadata = DocumentMetadata()
    assert metadata.tags == []

    # Test tag limit
    with pytest.raises(ValidationError):
        DocumentMetadata(tags=["tag"] * 51)

    # Test tag length
    with pytest.raises(ValidationError):
        DocumentMetadata(tags=["a" * 101])


def test_document_validation():
    """Test Document validation."""
    # Valid document
    doc = Document(text="This is a test document")
    assert doc.text == "This is a test document"

    # Document with metadata
    doc = Document(text="Test", metadata=DocumentMetadata(category="test"))
    assert doc.metadata.category == "test"

    # Empty text should fail
    with pytest.raises(ValidationError):
        Document(text="")

    # Whitespace-only text should fail
    with pytest.raises(ValidationError):
        Document(text="   ")

    # Text too long
    with pytest.raises(ValidationError):
        Document(text="a" * 100001)


def test_search_result_validation():
    """Test SearchResult validation."""
    result = SearchResult(
        id="test-id", text="Test text", metadata=DocumentMetadata(), score=0.95
    )
    assert result.id == "test-id"
    assert result.score == 0.95

    # Score must be between 0 and 1
    with pytest.raises(ValidationError):
        SearchResult(id="id", text="text", score=1.5)

    with pytest.raises(ValidationError):
        SearchResult(id="id", text="text", score=-0.1)


# ============================================================================
# Test: VectorMemory Initialization
# ============================================================================


@pytest.mark.asyncio
async def test_vector_memory_init(tmp_path):
    """Test VectorMemory initialization."""
    storage = tmp_path / "vectors"

    with patch("backend.cto.memory.vectors.VECTOR_DEPS_AVAILABLE", True):
        with patch("backend.cto.memory.vectors.EmbeddingModel"):
            memory = VectorMemory(persist_directory=storage)

            assert memory.persist_directory == storage
            assert not memory._initialized

            # Should raise error if operations are called before initialization
            with pytest.raises(RuntimeError, match="not initialized"):
                await memory.add_document("test")


@pytest.mark.asyncio
async def test_vector_memory_initialize(vector_storage):
    """Test VectorMemory initialize method."""
    with patch("backend.cto.memory.vectors.VECTOR_DEPS_AVAILABLE", True):
        with patch("backend.cto.memory.vectors.ChromaDBAdapter") as mock_adapter:
            with patch("backend.cto.memory.vectors.EmbeddingModel") as mock_embedding:
                mock_embed_instance = AsyncMock()
                mock_embed_instance._ensure_loaded = AsyncMock()
                mock_embedding.return_value = mock_embed_instance

                mock_store_instance = AsyncMock()
                mock_adapter.return_value = mock_store_instance

                memory = VectorMemory(persist_directory=vector_storage)
                await memory.initialize()

                assert memory._initialized
                assert memory._store is not None
                mock_embed_instance._ensure_loaded.assert_called_once()


@pytest.mark.asyncio
async def test_create_vector_memory_convenience():
    """Test create_vector_memory convenience function."""
    with patch("backend.cto.memory.vectors.VECTOR_DEPS_AVAILABLE", True):
        with patch("backend.cto.memory.vectors.ChromaDBAdapter"):
            with patch("backend.cto.memory.vectors.EmbeddingModel") as mock_embedding:
                mock_embed_instance = AsyncMock()
                mock_embed_instance._ensure_loaded = AsyncMock()
                mock_embedding.return_value = mock_embed_instance

                memory = await create_vector_memory()

                assert memory._initialized
                assert isinstance(memory, VectorMemory)


# ============================================================================
# Test: Add Document
# ============================================================================


@pytest.mark.asyncio
async def test_add_document_basic(vector_memory):
    """Test adding a document to vector memory."""
    doc_id = await vector_memory.add_document("This is a test document")

    assert doc_id is not None
    assert len(doc_id) > 0

    # Verify embedding was generated
    vector_memory._embedding_model.embed.assert_called_once()

    # Verify document was added to store
    vector_memory._store.add.assert_called_once()


@pytest.mark.asyncio
async def test_add_document_with_metadata(vector_memory):
    """Test adding a document with metadata."""
    metadata = {"source": "test.txt", "category": "test", "tags": ["python", "testing"]}

    doc_id = await vector_memory.add_document(
        "Test document with metadata", metadata=metadata
    )

    assert doc_id is not None

    # Verify metadata was passed to store
    call_args = vector_memory._store.add.call_args
    assert call_args is not None
    stored_metadata = call_args[0][3]  # 4th argument is metadata
    assert stored_metadata["category"] == "test"
    assert "python" in stored_metadata["tags"]


@pytest.mark.asyncio
async def test_add_document_invalid_text(vector_memory):
    """Test adding document with invalid text."""
    with pytest.raises(ValueError):
        await vector_memory.add_document("")

    with pytest.raises(ValueError):
        await vector_memory.add_document("   ")


@pytest.mark.asyncio
async def test_add_document_invalid_metadata(vector_memory):
    """Test adding document with invalid metadata."""
    with pytest.raises(ValidationError):
        await vector_memory.add_document(
            "Test", metadata={"tags": ["tag"] * 51}  # Too many tags
        )


# ============================================================================
# Test: Search
# ============================================================================


@pytest.mark.asyncio
async def test_search_basic(vector_memory):
    """Test basic search functionality."""
    # Mock search results
    vector_memory._store.search.return_value = [
        ("id1", "Document 1", {}, 0.95),
        ("id2", "Document 2", {"category": "test"}, 0.85),
    ]

    results = await vector_memory.search("test query")

    assert len(results) == 2
    assert results[0].id == "id1"
    assert results[0].score == 0.95
    assert results[1].id == "id2"
    assert results[1].metadata.category == "test"

    # Verify embedding was generated for query
    vector_memory._embedding_model.embed.assert_called()


@pytest.mark.asyncio
async def test_search_with_limit(vector_memory):
    """Test search with custom limit."""
    vector_memory._store.search.return_value = []

    await vector_memory.search("test query", limit=5)

    # Verify limit was passed to store
    call_args = vector_memory._store.search.call_args
    assert call_args[0][1] == 5  # Second argument is limit


@pytest.mark.asyncio
async def test_search_with_metadata_filter(vector_memory):
    """Test search with metadata filtering."""
    vector_memory._store.search.return_value = []

    metadata_filter = {"category": "test"}
    await vector_memory.search("test query", metadata_filter=metadata_filter)

    # Verify filter was passed to store
    call_args = vector_memory._store.search.call_args
    assert call_args[0][2] == metadata_filter


@pytest.mark.asyncio
async def test_search_invalid_query(vector_memory):
    """Test search with invalid query."""
    with pytest.raises(ValueError, match="Query cannot be empty"):
        await vector_memory.search("")

    with pytest.raises(ValueError, match="Query cannot be empty"):
        await vector_memory.search("   ")


@pytest.mark.asyncio
async def test_search_invalid_limit(vector_memory):
    """Test search with invalid limit."""
    with pytest.raises(ValueError, match="Limit must be between 1 and 100"):
        await vector_memory.search("test", limit=0)

    with pytest.raises(ValueError, match="Limit must be between 1 and 100"):
        await vector_memory.search("test", limit=101)


@pytest.mark.asyncio
async def test_search_empty_results(vector_memory):
    """Test search with no results."""
    vector_memory._store.search.return_value = []

    results = await vector_memory.search("nonexistent query")

    assert len(results) == 0
    assert isinstance(results, list)


# ============================================================================
# Test: Delete
# ============================================================================


@pytest.mark.asyncio
async def test_delete_document(vector_memory):
    """Test deleting a document."""
    doc_id = "test-id-123"

    await vector_memory.delete(doc_id)

    # Verify delete was called on store
    vector_memory._store.delete.assert_called_once_with(doc_id)


# ============================================================================
# Test: Count
# ============================================================================


@pytest.mark.asyncio
async def test_count_documents(vector_memory):
    """Test counting documents."""
    vector_memory._store.count.return_value = 42

    count = await vector_memory.count()

    assert count == 42
    vector_memory._store.count.assert_called_once()


@pytest.mark.asyncio
async def test_count_empty_store(vector_memory):
    """Test count with empty store."""
    vector_memory._store.count.return_value = 0

    count = await vector_memory.count()

    assert count == 0


# ============================================================================
# Test: Error Handling
# ============================================================================


@pytest.mark.asyncio
async def test_operations_without_initialization(tmp_path):
    """Test that operations fail without initialization."""
    with patch("backend.cto.memory.vectors.VECTOR_DEPS_AVAILABLE", True):
        with patch("backend.cto.memory.vectors.EmbeddingModel"):
            memory = VectorMemory(persist_directory=tmp_path / "vectors")

            with pytest.raises(RuntimeError, match="not initialized"):
                await memory.add_document("test")

            with pytest.raises(RuntimeError, match="not initialized"):
                await memory.search("test")

            with pytest.raises(RuntimeError, match="not initialized"):
                await memory.delete("test-id")

            with pytest.raises(RuntimeError, match="not initialized"):
                await memory.count()


@pytest.mark.asyncio
async def test_import_error_handling():
    """Test behavior when vector dependencies are not available."""
    with patch("backend.cto.memory.vectors.VECTOR_DEPS_AVAILABLE", False):
        from backend.cto.memory.vectors import ChromaDBAdapter, EmbeddingModel

        # ChromaDBAdapter should raise ImportError
        with pytest.raises(
            ImportError, match="Vector database dependencies not installed"
        ):
            ChromaDBAdapter()

        # EmbeddingModel should raise ImportError
        with pytest.raises(ImportError, match="Embedding dependencies not installed"):
            EmbeddingModel()


# ============================================================================
# Test: Concurrent Operations
# ============================================================================


@pytest.mark.asyncio
async def test_concurrent_add_operations(vector_memory):
    """Test multiple concurrent add operations."""
    tasks = [vector_memory.add_document(f"Document {i}") for i in range(10)]

    doc_ids = await asyncio.gather(*tasks)

    assert len(doc_ids) == 10
    assert len(set(doc_ids)) == 10  # All IDs should be unique


@pytest.mark.asyncio
async def test_concurrent_search_operations(vector_memory):
    """Test multiple concurrent search operations."""
    vector_memory._store.search.return_value = []

    tasks = [vector_memory.search(f"query {i}") for i in range(5)]

    results = await asyncio.gather(*tasks)

    assert len(results) == 5


# ============================================================================
# Test: Integration Scenarios
# ============================================================================


@pytest.mark.asyncio
async def test_add_search_delete_workflow(vector_memory):
    """Test complete workflow: add, search, delete."""
    # Mock search to return the added document
    added_doc_id = None

    async def mock_search(embedding, limit, filter=None):
        if added_doc_id:
            return [(added_doc_id, "Machine learning is a subset of AI", {}, 0.95)]
        return []

    vector_memory._store.search.side_effect = mock_search

    # Add document
    added_doc_id = await vector_memory.add_document(
        "Machine learning is a subset of AI"
    )
    assert added_doc_id is not None

    # Search for it
    results = await vector_memory.search("What is ML?")
    assert len(results) == 1
    assert results[0].id == added_doc_id

    # Delete it
    await vector_memory.delete(added_doc_id)
    vector_memory._store.delete.assert_called_with(added_doc_id)


@pytest.mark.asyncio
async def test_multiple_documents_search(vector_memory):
    """Test searching across multiple documents."""
    # Mock search results with multiple documents
    vector_memory._store.search.return_value = [
        ("id1", "Python is a programming language", {"category": "programming"}, 0.92),
        ("id2", "Machine learning with Python", {"category": "ai"}, 0.88),
        ("id3", "Python web development", {"category": "web"}, 0.75),
    ]

    results = await vector_memory.search("Python programming", limit=10)

    assert len(results) == 3
    assert results[0].score >= results[1].score >= results[2].score  # Sorted by score
    assert all(isinstance(r, SearchResult) for r in results)


# ============================================================================
# Test: Edge Cases
# ============================================================================


@pytest.mark.asyncio
async def test_add_very_long_document(vector_memory):
    """Test adding a document at maximum length."""
    long_text = "a" * 100000  # Max allowed length

    doc_id = await vector_memory.add_document(long_text)
    assert doc_id is not None


@pytest.mark.asyncio
async def test_search_with_special_characters(vector_memory):
    """Test search with special characters."""
    vector_memory._store.search.return_value = []

    # Should not raise errors
    await vector_memory.search("test @#$%^&*()")
    await vector_memory.search("test\nwith\nnewlines")
    await vector_memory.search("test with émojis 🎉")


@pytest.mark.asyncio
async def test_metadata_with_none_values(vector_memory):
    """Test adding document with None metadata values."""
    metadata = {"source": None, "category": "test", "tags": []}

    doc_id = await vector_memory.add_document("Test document", metadata=metadata)
    assert doc_id is not None

    # Verify None values are excluded
    call_args = vector_memory._store.add.call_args
    stored_metadata = call_args[0][3]
    assert "source" not in stored_metadata  # None values should be excluded
    assert stored_metadata["category"] == "test"

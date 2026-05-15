"""Test placeholder for FRIDAY."""


def test_friday_imports():
    import friday
    assert friday.__version__ == "0.1.0"
    assert friday.__license__ == "MIT"


def test_memory_tree():
    from friday.memory.memory_tree import MemoryTree
    
    # Use in-memory DB for test
    tree = MemoryTree(db_path=":memory:")
    
    # Add a chunk
    chunk_id = tree.add_chunk(
        source="test",
        type_="email",
        content="Hello from test",
        summary="Test summary",
        tags=["test"]
    )
    assert chunk_id == 1
    
    # Query it back
    results = tree.query(["test"])
    assert len(results) == 1
    assert results[0]["content"] == "Hello from test"
    assert results[0]["summary"] == "Test summary"

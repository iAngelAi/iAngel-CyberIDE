"""
Sample test file to validate test infrastructure.
"""


def test_sample_pass():
    """A passing test to light up the neural circuits."""
    assert True, "This test always passes"


def test_basic_math():
    """Test basic arithmetic."""
    assert 1 + 1 == 2
    assert 2 * 3 == 6


def test_with_fixture(sample_data):
    """Test using a fixture."""
    assert sample_data["test_value"] == 42
    assert "Neural" in sample_data["test_string"]

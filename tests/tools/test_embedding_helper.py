import pytest
import numpy as np
from unittest.mock import patch
from ebiose.tools.embedding_helper import (
    generate_embeddings,
    embedding_distance,
    generate_fake_embedding,
    generate_embeddings_impl,
)

@patch("ebiose.tools.embedding_helper.generate_fake_embedding")
def test_generate_embeddings_fake(mock_fake_embedding):
    generate_embeddings("test")
    mock_fake_embedding.assert_called_once()

@patch("ebiose.tools.embedding_helper.generate_embeddings_impl")
def test_generate_embeddings_impl_toggle(mock_impl):
    with patch("ebiose.tools.embedding_helper.fake", False):
        generate_embeddings("test")
    mock_impl.assert_called_once_with("test")

def test_embedding_distance():
    a = np.array([1, 0])
    b = np.array([0, 1])
    assert np.isclose(embedding_distance(a, b), 1.0)

    c = np.array([1, 1])
    d = np.array([1, 1])
    assert np.isclose(embedding_distance(c, d), 0.0)

def test_generate_fake_embedding():
    embedding = generate_fake_embedding(128)
    assert embedding.shape == (128,)
    assert np.isclose(np.linalg.norm(embedding), 1.0)

def test_generate_embeddings_impl_raises_error():
    with pytest.raises(NotImplementedError):
        generate_embeddings_impl("test")

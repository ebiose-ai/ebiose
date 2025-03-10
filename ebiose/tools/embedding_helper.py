"""Copyright (c) 2024, Inria.

Pre-release Version - DO NOT DISTRIBUTE
This software is licensed under the MIT License. See LICENSE for details.
"""

import numpy as np


def generate_embeddings(text: str) -> np.ndarray:
    fake = True
    if fake:
        return generate_fake_embedding()
    return generate_embeddings_impl(text)

def embedding_distance(emb_a: np.ndarray, emb_b: np.ndarray) -> float:
    return 1 - np.dot(emb_a, emb_b) / (np.linalg.norm(emb_a) * np.linalg.norm(emb_b))

def generate_fake_embedding(dimension: int=1536) -> np.ndarray:
    rng = np.random.default_rng()
    fake_embedding = rng.random(dimension)
    return fake_embedding / np.linalg.norm(fake_embedding)

def generate_embeddings_impl(text: str) -> np.ndarray:
    msg = "This function is not implemented yet"
    raise NotImplementedError(msg)

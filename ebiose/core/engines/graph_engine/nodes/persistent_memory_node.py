"""Copyright (c) 2024, Inria.

Pre-release Version - DO NOT DISTRIBUTE
This software is licensed under the MIT License. See LICENSE for details.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import ClassVar, Literal

import numpy as np
from loguru import logger
from pydantic import BaseModel, Field, model_validator

from ebiose.core.engines.graph_engine.nodes.node import BaseNode
from ebiose.tools.embedding_helper import embedding_distance, generate_embeddings


class PersistentMemoryNodeState(BaseModel):
    operation: Literal["read", "write"]
    content: str | None = None
    query: str | None = None
    top_k: int = 3
    results: list[str] | None = None

    @model_validator(mode="after")
    def validate_operation_requirements(self):
        """Validate that required fields are present based on operation type."""
        if self.operation == "write" and not self.content:
            msg = "content is required for write operation"
            raise ValueError(msg)
        if self.operation == "read" and not self.query:
            msg = "query is required for read operation"
            raise ValueError(msg)
        return self


class PersistentMemoryNode(BaseNode):
    """The PersistentMemoryNode allows agents to store and retrieve information across executions.
    
    This node provides persistent memory capabilities using semantic search over stored content.
    It supports two operations:
    - 'write': Store content with its semantic embedding for later retrieval
    - 'read': Retrieve the most semantically similar content based on a query
    
    Use this node when agents need to:
    - Remember information from previous executions
    - Learn from past experiences
    - Build up knowledge over multiple runs
    - Share information between different agent instances
    
    Attributes:
        id: The identifier of the node
        name: The name of the node
        purpose: Description of what the node does
        type: The type of the node (PersistentMemoryNode)
        memory_file: Path to the JSON file storing the memory (default: "memory.json")
    """

    id: str = "persistent_memory_node"
    name: str = "Persistent Memory Node"
    purpose: str = "A node for reading from and writing to a persistent memory store using semantic search."
    type: Literal["PersistentMemoryNode"] = "PersistentMemoryNode"
    memory_file: str = Field(default="memory.json", description="Path to the memory storage file")

    async def call_node(self, state: PersistentMemoryNodeState, context=None) -> dict:
        """Execute the memory operation (read or write).
        
        Args:
            state: The input state containing operation type and parameters
            context: Optional context (unused but required by interface)
            
        Returns:
            dict: Empty dict for write, or dict with 'results' key for read
        """
        try:
            if state.operation == "write":
                self._write_to_memory(state.content)
                return {}
            elif state.operation == "read":
                results = self._read_from_memory(state.query, state.top_k)
                return {"results": results}
            else:
                msg = f"Unknown operation: {state.operation}"
                raise ValueError(msg)
        except Exception as e:
            logger.error(f"Error in PersistentMemoryNode: {e!s}")
            return {"results": [], "error": str(e)}

    def _read_from_memory(self, query: str, top_k: int) -> list[str]:
        """Read the top_k most similar entries from memory based on semantic similarity.
        
        Args:
            query: The search query
            top_k: Number of results to return
            
        Returns:
            list[str]: List of content strings, ordered by similarity
        """
        if not Path(self.memory_file).exists():
            logger.debug(f"Memory file {self.memory_file} does not exist, returning empty results")
            return []

        try:
            query_embedding = generate_embeddings(query)
            
            with Path(self.memory_file).open("r") as f:
                memory_data = json.load(f)

            if not memory_data:
                return []

            # Calculate distances and sort
            for entry in memory_data:
                entry["embedding"] = np.array(entry["embedding"])
                entry["distance"] = embedding_distance(query_embedding, entry["embedding"])

            memory_data.sort(key=lambda x: x["distance"])
            
            return [entry["content"] for entry in memory_data[:top_k]]
        except Exception as e:
            logger.error(f"Error reading from memory: {e!s}")
            return []

    def _write_to_memory(self, content: str) -> None:
        """Write content to memory with its semantic embedding.
        
        Args:
            content: The content to store
        """
        try:
            # Ensure directory exists
            memory_path = Path(self.memory_file)
            memory_path.parent.mkdir(parents=True, exist_ok=True)

            # Initialize file if it doesn't exist
            if not memory_path.exists():
                with memory_path.open("w") as f:
                    json.dump([], f)

            # Generate embedding
            embedding = generate_embeddings(content)
            
            # Read existing data
            with memory_path.open("r") as f:
                memory_data = json.load(f)

            # Append new entry
            memory_data.append({
                "content": content,
                "embedding": embedding.tolist() if isinstance(embedding, np.ndarray) else embedding,
            })

            # Write back with proper truncation
            with memory_path.open("w") as f:
                json.dump(memory_data, f, indent=2)
                
            logger.debug(f"Successfully wrote to memory: {content[:50]}...")
        except Exception as e:
            logger.error(f"Error writing to memory: {e!s}")
            raise

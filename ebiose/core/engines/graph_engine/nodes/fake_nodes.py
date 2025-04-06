"""Copyright (c) 2024, Inria.

Pre-release Version - DO NOT DISTRIBUTE
This software is licensed under the MIT License. See LICENSE for details.
"""

from __future__ import annotations

import abc
from typing import Literal

from pydantic import BaseModel, Field

from ebiose.core.engines.graph_engine.nodes.node import BaseNode


class PythonNode(BaseNode):
    """
    The PythonNode executes raw or templated Python code in a controlled environment.
    It enables dynamic logic, algorithmic computation, or custom scripting directly within the graph.
    Inputs can be passed as variables into the code block, and outputs are returned as structured data.
    """
    type: Literal["PythonNode"] = "PythonNode"

    async def call_node(self, agent_state: BaseModel | dict, config: BaseModel | None = None) -> dict:
        pass


class DatabaseNode(BaseNode):
    """
    The DatabaseNode connects to a structured data store (SQL, NoSQL, etc.) and executes queries.
    Inputs can dynamically modify queries or bind parameters. The resulting records are returned for downstream use.
    """
    type: Literal["DatabaseNode"] = "DatabaseNode"

    async def call_node(self, agent_state: BaseModel | dict, config: BaseModel | None = None) -> dict:
        pass


class APINode(BaseNode):
    """
    The APINode is a bridge to external HTTP APIs. It constructs requests from inputs,
    sends them to the specified endpoint, and parses the responses for downstream processing.
    It supports GET, POST, and other HTTP methods, with customizable headers and authentication.
    """
    type: Literal["APINode"] = "APINode"

    async def call_node(self, agent_state: BaseModel | dict, config: BaseModel | None = None) -> dict:
        pass


class WebScraperNode(BaseNode):
    """
    The WebScraperNode retrieves content from specified URLs and extracts relevant information.
    Useful for retrieving real-time data from websites or augmenting LLM input with up-to-date content.
    """
    type: Literal["WebScraperNode"] = "WebScraperNode"

    async def call_node(self, agent_state: BaseModel | dict, config: BaseModel | None = None) -> dict:
        pass


class FileNode(BaseNode):
    """
    The FileNode interacts with file systems or blob storage. It can read input files (e.g. CSV, JSON, PDF),
    parse them, and route their contents to downstream nodes. It can also write intermediate or final results.
    """
    type: Literal["FileNode"] = "FileNode"

    async def call_node(self, agent_state: BaseModel | dict, config: BaseModel | None = None) -> dict:
        pass

class UserQueryNode(BaseNode):
    """
    The UserQueryNode interrupts the graph flow to ask a question or prompt to the user.
    It is useful when human feedback, validation, or clarification is required before continuing
    the graph execution. This enables human-in-the-loop workflows or interactive agents.
    """
    type: Literal["UserQueryNode"] = "UserQueryNode"

    async def call_node(self, agent_state: BaseModel | dict, config: BaseModel | None = None) -> dict:
        pass

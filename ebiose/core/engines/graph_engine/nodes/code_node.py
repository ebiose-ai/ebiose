"""Copyright (c) 2024, Inria.

Pre-release Version - DO NOT DISTRIBUTE
This software is licensed under the MIT License. See LICENSE for details.
"""

from __future__ import annotations

import ast
from typing import Literal

from pydantic import BaseModel, Field

from ebiose.core.engines.graph_engine.nodes.node import BaseNode


class CodeNode(BaseNode):
    """The CodeNode class represents a node that executes code using Python's exec function."""

    type: Literal["CodeNode"] = "CodeNode"
    code_key: str = Field(default="last_message", description="The key in the state where the code is stored")

    async def call_node(self, state: BaseModel | dict) -> dict:
        """Executes the code from the last message in the state using exec and returns the result."""
        # Retrieve the last message from the state
        last_message = state.get("messages", [])[-1] if isinstance(state, dict) else getattr(state, "messages", [])[-1]
        code = last_message.get(self.code_key) if isinstance(last_message, dict) else getattr(last_message, self.code_key)

        # Basic static analysis to prevent dangerous code
        if not self.is_safe_code(code):
            msg="Unsafe code detected"
            raise ValueError(msg)

        # Execute the code
        local_vars = {}
        exec(code, {}, local_vars)  # noqa: S102
        return {"result": local_vars}

    def is_safe_code(self, code: str) -> bool:
        """Perform basic static analysis to check for unsafe code."""
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import | ast.ImportFrom | ast.Exec):
                    return False
        except SyntaxError:
            return False
        else:
            return True

from __future__ import annotations

from typing import Literal

from ebiose.core.engines.graph_engine.nodes.node import BaseNode


class RegexRoutingNode(BaseNode):
    type: Literal["RegexRoutingNode"] = "RegexRoutingNode"

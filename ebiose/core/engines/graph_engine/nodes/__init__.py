import importlib
from functools import reduce

from pydantic import BaseModel

from ebiose.core.engines.graph_engine.nodes.llm_node import LLMNode  # noqa: F401
from ebiose.core.engines.graph_engine.nodes.fake_nodes import (  # noqa: F401
    PythonNode,
    DatabaseNode,
    APINode,
    WebScraperNode,
    FileNode,
)
    
from ebiose.core.engines.graph_engine.nodes.node import (  # noqa: F401
    BaseNode,
    EndNode,
    StartNode,
)
from ebiose.core.engines.graph_engine.nodes.pydantic_validator_node import (
    PydanticValidatorNode,  # noqa: F401
)
from ebiose.core.engines.graph_engine.nodes.routing_node import (
    RoutingNode,  # noqa: F401
)


def get_all_subclasses(cls: BaseModel) -> list:
    """This function get all subclasses of a class recursively.

    Its purpose is to provide the Union type representing all node types, in use in the Graph class.
    """
    all_subclasses = []
    for subclass in cls.__subclasses__():
        all_subclasses.append(subclass)
        all_subclasses.extend(get_all_subclasses(subclass))
    return all_subclasses


# Import the module containing the node types
nodes_module = importlib.import_module("ebiose.core.engines.graph_engine.nodes")

# Get all subclasses of BaseNode
node_types = get_all_subclasses(BaseNode)

# Build a list of names of node types
node_types_names = [node_type.__name__ for node_type in node_types]

# Build a map from string names to types
node_types_map = {node_type.__name__: node_type for node_type in node_types}

# Remove BaseNode itself if it's in the list
if BaseNode in node_types:
    node_types.remove(BaseNode)

# Create the NodeTypes union from the node types list
NodeTypes = reduce(lambda acc, t: acc | t, node_types)

def get_node_types_docstrings(node_types_names: list) -> str:
    """Get the docstring of each node type to pass in the prompts."""
    docstrings_list = []
    for node_type_name in node_types_names:
        node_type = node_types_map.get(node_type_name)
        if node_type:
            docstring = node_type.__doc__
            if docstring:
                docstrings_list.append(f"**{node_type_name}**:\n{docstring}\n")
    return "\n".join(docstrings_list)

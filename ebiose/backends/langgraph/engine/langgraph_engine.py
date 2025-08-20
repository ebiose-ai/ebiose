"""Copyright (c) 2024, Inria.

Pre-release Version - DO NOT DISTRIBUTE
This software is licensed under the MIT License. See LICENSE for details.
"""

from __future__ import annotations

from collections.abc import Sequence  # noqa: TC003
from typing import Self

from langfuse import observe, get_client
from langfuse import Langfuse
from langfuse.langchain import CallbackHandler
from langgraph.graph import StateGraph
from langgraph.graph import END, START
from langgraph.pregel import Pregel
from loguru import logger
from pydantic import (
    BaseModel,
    Field,
    PrivateAttr,
    ValidationError,
    create_model,
    field_serializer,
    field_validator,
    model_validator,
)

from ebiose.backends.langgraph.engine.llm_node import LangGraphLLMNode
from ebiose.backends.langgraph.engine.states import (
    LangGraphEngineContext,
)
from ebiose.backends.langgraph.engine.utils import GraphUtils, get_path
from ebiose.core.engines.graph_engine.graph import Graph
from ebiose.core.engines.graph_engine.graph_engine import GraphEngine
from ebiose.core.engines.graph_engine.nodes.llm_node import LLMNode
from ebiose.core.engines.graph_engine.nodes.node import EndNode, StartNode
from ebiose.tools.json_schema_to_pydantic import create_pydantic_model_from_schema

# TODO(xabier): replace when langfuse is updated to >=3.0
# langfuse = get_client()
# langfuse_handler = CallbackHandler()

class LangGraphEngine(GraphEngine):
    engine_type: str = "langgraph_engine"
    model_endpoint_id: str | None = None
    recursion_limit: int = Field(default=15)
    # TODO(xabier): remove tags, should now use agent_type instead
    tags: Sequence[str] = ["agent"]

    _compiled_graph: Pregel | None = PrivateAttr(None)
    _state: type[BaseModel] | None = PrivateAttr(None)
    _context: BaseModel | None = PrivateAttr(None)


    @model_validator(mode="after")
    def _set_llm_models(self) -> Self:
        if self.input_model is None:
            self.input_model = create_pydantic_model_from_schema(
                self.configuration["input_model"],
                model_name="InputModel",
            )
        if self.output_model is None:
            self.output_model = create_pydantic_model_from_schema(
                self.configuration["output_model"],
                model_name="OutputModel",
            )
        if self.graph is None:
            self.graph = Graph.model_validate(self.configuration["graph"])

        for i, node in enumerate(self.graph.nodes):
            if isinstance(node, LLMNode):
                # TODO(xabier): improve the way temperature and tools are passed to the LLM configuration
                if node.model_extra is not None:
                    temperature = node.model_extra.get("temperature", 0.7)
                    tools = node.model_extra.get("tools", [])
                temp_node = LangGraphLLMNode(
                    id=node.id,
                    name=node.name,
                    purpose=node.purpose,
                    prompt=node.prompt,
                    model_endpoint_id=self.model_endpoint_id,
                    temperature=temperature,
                    tools=tools,
                )
                self.graph.nodes[i] = temp_node

        return self

    @observe(name="run_agent_engine")
    async def _run_implementation(self, agent_input: BaseModel, master_agent_id: str, forge_cycle_id: str | None = None,  **kwargs: dict[str, any]) -> BaseModel | dict | None:

        final_state = await self.invoke_graph(agent_input, forge_cycle_id=forge_cycle_id)

        if "output" in final_state and final_state["output"] is not None:
            return  final_state["output"]

        if self.output_model is not None:
            try:
                return self.output_model.model_validate(final_state)
            except ValidationError:
                pass

            structured_output_agent = GraphUtils.get_structured_output_agent(
                self.output_model,
            )
            so_agent_input = structured_output_agent.agent_engine.input_model(
                last_message=final_state["messages"][-1],
            )

            try:
                return await structured_output_agent.run(so_agent_input, master_agent_id, forge_cycle_id=forge_cycle_id)
            except Exception as e:
                logger.debug(f"Error while running agent {self.agent_id}, when calling structured output agent: {e!s}")
        else:
            return final_state

    def _build_state(self) -> None:
        """Build dynamically the state of the agent with the nodes of the graph.

        For each nodes it creates a node_id_prompt, node_it_responses where all responses are stored,
        """
        if self._state is not None:
            return

        base_classes = set()
        for node in self.graph.nodes:
            if isinstance(node, StartNode | EndNode):
                continue
            base_classes.add(node.input_state_model)
            base_classes.add(node.output_state_model)

        self._state = type("State", tuple(base_classes), {})

    def _build_context(self, forge_cycle_id: str | None = None) -> BaseModel:
        """Build dynamically the context of the agent with the nodes of the graph."""
        if self._context is not None:
            return self._context

        fields = {
            "agent_id": (str, Field(default=self.agent_id)),
            "forge_cycle_id": (str | None, Field(default=None)),
        }
        for node in self.graph.nodes:
            if isinstance(node, LLMNode):
                fields[node.id] = (dict, {})

        # Use create_model to dynamically create the Config model
        self._context = create_model(
            "Config",
            __base__=LangGraphEngineContext,
            **fields,
        )

        return self._context

    @observe(name="invoke_graph")
    async def invoke_graph(
            self,
            agent_input: BaseModel,
            forge_cycle_id: str | None = None,
        ) -> BaseModel:
            """Compile and run the agent.

            Args:
                agent_input: The input that goes in first trough the graph

            Returns: the final updated graph state
            """
            compiled_graph = await self._compile_graph(forge_cycle_id=forge_cycle_id)
            initial_state = self._state(
                input=agent_input,
                **agent_input.model_dump(),
            )

            node_config = {}
            for node in self.graph.nodes:
                outgoing_conditional_edges = self.graph.get_outgoing_edges(
                    node.id,
                    conditional=True,
                )
                if len(outgoing_conditional_edges) > 0:
                    node_config[node.id] = {
                        "output_conditions": [edge.condition for edge in outgoing_conditional_edges],
                    }
            
            langfuse_handler = CallbackHandler()
            config = {
                "callbacks": [langfuse_handler],
                "metadata": {
                    "langfuse_session_id": str(self.agent_id),
                    "langfuse_tags": self.tags,
                    "agent_id": self.agent_id,
                    "forge_cycle_id": forge_cycle_id,
                },
            }
            
            context = self._context(
                shared_context_prompt=self.graph.shared_context_prompt, #.format(**agent_input.model_dump()),
                model_endpoint_id=self.model_endpoint_id,
                output_model=self.output_model,
                recursion_limit = self.recursion_limit,
                forge_cycle_id=forge_cycle_id,
                **node_config,
            )
            

            return await compiled_graph.ainvoke(
                initial_state,
                config=config,
                context=context.model_dump(),
            )

    async def _compile_graph(self, forge_cycle_id: str | None=None) -> Pregel:
            """Compile the agent into a runnable graph."""
            if self._compiled_graph is None:
                self._build_state()
                self._build_context(forge_cycle_id=forge_cycle_id)
                self._compiled_graph = await self.__to_compiled_graph()
            return self._compiled_graph

    def __to_workflow(self) -> StateGraph:

        workflow = StateGraph(
            state_schema=self._state, 
            context_schema=self._context,
            # TODO(xabier): test the use of input_model and output_model as I/O schemas
            # input_schema=self.input_model,
            # output_schema=self.output_model,
        )

        # add nodes to the workflow
        nodes_dict = {node.id: node for node in self.graph.nodes}
        for node_id, node in nodes_dict.items():
            if isinstance(node, EndNode | StartNode):
                continue
            # We first retrieve the function that represents the node it does not depend
            # if we have a llm, a rag or whatnot
            workflow.add_node(node_id, node.call_node)

        # add edges to the workflow
        for node_id, node in nodes_dict.items():
            if isinstance(node, EndNode):
                continue

            # ---------------------- Not conditional edges ----------------------------
            outgoing_nodes = self.graph.get_outgoing_nodes(
                node_id,
                conditional=False,
            )
            outgoing_node_ids = [
                node.id if not isinstance(node, EndNode) else END
                for node in outgoing_nodes
            ]

            for outgoing_nodes_id in outgoing_node_ids:
                workflow.add_edge(
                    node_id if not isinstance(node, StartNode) else START,
                    outgoing_nodes_id,
                )

            # -----------------------Conditional edges ---------------------
            # we get the destination node of the current node that pass through a conditional edge
            # along with their corresponding condition
            # get_outgoing_edges(self: Self, node_id: str, conditional: Optional[bool]=None)
            outgoing_conditional_edges = self.graph.get_outgoing_edges(
                node_id,
                conditional=True,
            )
            if not outgoing_conditional_edges:
                continue
            path, path_map = get_path(
                outgoing_conditional_edges,
                self.graph.get_end_node_id(),
            )

            workflow.add_conditional_edges(
                source=node_id,
                path=path,
                path_map=path_map,
            )

        return workflow

    async def __to_compiled_graph(self) -> Pregel:
        """Compile an agent into a runnable graph."""
        return self.__to_workflow().compile()

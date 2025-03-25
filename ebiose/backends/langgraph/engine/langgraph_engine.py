"""Copyright (c) 2024, Inria.

Pre-release Version - DO NOT DISTRIBUTE
This software is licensed under the MIT License. See LICENSE for details.
"""

from __future__ import annotations

from collections.abc import Sequence  # noqa: TC003
from typing import Self

from langfuse.decorators import langfuse_context, observe
from langgraph.graph import StateGraph
from langgraph.graph.graph import END, START, CompiledGraph
from loguru import logger
from pydantic import (
    BaseModel,
    Field,
    PrivateAttr,
    ValidationError,
    create_model,
    model_validator,
)

from ebiose.backends.langgraph.engine.llm_node import LangGraphLLMNode
from ebiose.backends.langgraph.engine.states import (
    LangGraphEngineConfig,
)
from ebiose.backends.langgraph.engine.utils import GraphUtils, get_path
from ebiose.core.engines.graph_engine.graph_engine import GraphEngine
from ebiose.core.engines.graph_engine.nodes.llm_node import LLMNode
from ebiose.core.engines.graph_engine.nodes.node import EndNode, StartNode


class LangGraphEngine(GraphEngine):
    engine_type: str = "langgraph_engine"
    model_endpoint_id: str | None = None
    recursion_limit: int = Field(default=15)
    tags: Sequence[str] = ["agent"]

    _compiled_graph: CompiledGraph | None = PrivateAttr(None)
    _state: type[BaseModel] | None = PrivateAttr(None)
    _config: BaseModel | None = PrivateAttr(None)

    @model_validator(mode="after")
    def _set_llm_models(self) -> Self:
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
    async def _run_implementation(self, agent_input: BaseModel, compute_token_id: str) -> BaseModel | dict | None:

        final_state = await self.invoke_graph(agent_input, compute_token_id)

        if "output" in final_state and final_state["output"] is not None:
            return  final_state["output"]

        if self.output_model is not None:
            try:
                return self.output_model.model_validate(final_state)
            except ValidationError:
                pass

            structured_output_agent = GraphUtils.get_structured_output_agent(self.output_model, self.model_endpoint_id)
            so_agent_input = structured_output_agent.agent_engine.input_model(
                last_message=final_state["messages"][-1],
            )

            try:
                return await structured_output_agent.run(so_agent_input, compute_token_id)
            except Exception as e:
                logger.debug(f"Error while running agent {self.id}, when calling structured output agent: {e!s}")
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

    def _build_config(self) -> BaseModel:
        """Build dynamically the config of the agent with the nodes of the graph."""
        if self._config is not None:
            return self._config

        fields = {}
        for node in self.graph.nodes:
            if isinstance(node, LLMNode):
                fields[node.id] = (dict, {})

        # Use create_model to dynamically create the Config model
        self._config = create_model(
            "Config",
            __base__=LangGraphEngineConfig,
            **fields,
        )

        return self._config


    async def invoke_graph(
            self,
            agent_input: BaseModel,
            compute_token_id: str,
        ) -> BaseModel:
            """Compile and run the agent.

            Args:
                agent_input: The input that goes in first trough the graph
                compute_token_id: The compute token id

            Returns: the final updated graph state
            """
            compiled_graph = await self._compile_graph()
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

            if len(self.tags) > 0:
                langfuse_context.update_current_trace(
                    tags=self.tags,
                )
            handler = langfuse_context.get_current_langchain_handler()
            config = self._config(
                shared_context_prompt=self.graph.shared_context_prompt, #.format(**agent_input.model_dump()),
                compute_token=compute_token_id,
                model_endpoint_id=self.model_endpoint_id,
                output_model=self.output_model,
                callbacks = [handler],
                recursion_limit = self.recursion_limit,
                **node_config,
            )

            return await compiled_graph.ainvoke(
                initial_state,
                config=config.model_dump(),
            )

    async def _compile_graph(self) -> CompiledGraph:
            """Compile the agent into a runnable graph."""
            if self._compiled_graph is None:
                self._build_state()
                self._build_config()
                self._compiled_graph = await self.__to_compiled_graph()
            return self._compiled_graph

    def __to_workflow(self) -> StateGraph:

        workflow = StateGraph(self._state, self._config)

        # add nodes to the workflow
        nodes_dict = {node.id: node for node in self.graph.nodes}
        for node_id, node in nodes_dict.items():
            if isinstance(node, EndNode | StartNode):
                continue
            # We first retrieve the function that represents the node it does not depend
            # if we have a llm, a rag or whatnot
            # TODO(xabier): can also use keywprd arguments metadata, input and retry
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

    async def __to_compiled_graph(self) -> CompiledGraph:
        """Compile an agent into a runnable graph."""
        return self.__to_workflow().compile()

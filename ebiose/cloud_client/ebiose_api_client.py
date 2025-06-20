
import functools
import json
import random
import re
from typing import TYPE_CHECKING
import uuid

from ebiose.cloud_client.client import AgentEngineInputModel, AgentInputModel, AgentType, EbioseCloudClient, EbioseCloudError, EcosystemOutputModel, ForgeCycleInputModel, ForgeInputModel, LogEntryInputModel
from ebiose.core.agent_factory import AgentFactory
from ebiose.core.ecosystem import Ecosystem
from ebiose.core.engines.graph_engine.utils import GraphUtils
from ebiose.core.model_endpoint import ModelEndpoints
if TYPE_CHECKING:
    from ebiose.core.forge_cycle import CloudForgeCycleConfig
    from ebiose.core.agent import Agent

from uuid import uuid4

ES_INDEX = "test-pva4"

def format_agent(agent: "Agent") -> AgentInputModel:
    """Format the agent for the API."""
    agent_engine = AgentEngineInputModel(
        engineType=agent.agent_engine.engine_type,
        configuration=agent.agent_engine.serialize_configuration(),
    )
    # TODO(xabier): make this more straightforward
    if agent.agent_type == "architect":
        agent_type = AgentType(2)
    elif agent.agent_type == "genetic_operator":
        agent_type = AgentType(1)
    else:
        agent_type = AgentType(0)
    return AgentInputModel(
        # uuid=agent.id,
        name=agent.name,
        description=agent.description,
        architectAgentUuid=agent.architect_agent_id,
        geneticOperatorAgentUuid=agent.genetic_operator_agent_id,
        agentEngine=agent_engine,
        descriptionEmbedding=agent.description_embedding,
        agentType=agent_type,
    )

def build_agent_input_model(agent: "Agent") -> AgentInputModel:
    """Build the AgentInputModel from the Agent."""
    agent_engine_input_model = AgentEngineInputModel(
        engine_type=agent.agent_engine.engine_type,
        configuration=agent.agent_engine.model_dump_json(),
    )
    return AgentInputModel(
        uuid=agent.id, # TODO(gildas): add this field to the server side
        name=agent.name,
        description=agent.description,
        agent_engine=agent_engine_input_model,
        architect_agent_uuid=agent.architect_agent_id,
        genetic_operator_agent_uuid=agent.genetic_operator_agent_id,
        description_embedding=None,
        # description_embedding=agent.description_embedding, # TODO(gildas): add this field as list of float to the server side
    )


class EbioseAPIClient:
    _client: EbioseCloudClient | None = None

    @classmethod
    def set_client(cls) -> None:
        """Set the API client with the provided API key."""
        if cls._client is None:
            cls._client = EbioseCloudClient(
                base_url=ModelEndpoints.get_ebiose_api_base(),
                api_key=ModelEndpoints.get_ebiose_api_key(),
            )

    import re

    @staticmethod
    def _to_snake_case(name: str) -> str:
        """Converts a PascalCase or camelCase string to snake_case."""
        # Example: "EcosystemUuid" -> "ecosystem_uuid"
        # Example: "Region" -> "region"
        # This regex finds a lowercase letter or digit followed by an uppercase letter
        # and inserts an underscore between them.
        s1 = re.sub(r'(.)([A-Z][a-z]+)', r'\1_\2', name)
        # This handles cases like "UUID" -> "_UUID", then we handle the rest.
        s2 = re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', s1)
        return s2.lower()

    @classmethod
    def _convert_data_keys(cls, data: any) -> any:
        """
        Recursively traverses a data structure (dict or list) and converts
        all dictionary keys from PascalCase to snake_case.
        """
        if isinstance(data, list):
            # If it's a list, apply the conversion to each item in the list.
            return [cls._convert_data_keys(item) for item in data]
        
        if isinstance(data, dict):
            # If it's a dictionary, create a new dict with converted keys.
            # Recursively call the function on values to handle nested structures.
            return {
                cls._to_snake_case(key): cls._convert_data_keys(value)
                for key, value in data.items()
            }
        
        # If it's not a list or dict, return the data as is.
        return data

    # This is the updated decorator within YourClass
    def _handle_api_errors(func):
        """
        Decorator to handle client initialization, API errors, AND
        to convert response keys from PascalCase to snake_case.
        """
        @functools.wraps(func)
        def wrapper(cls, *args, **kwargs):
            try:
                if cls._client is None:
                    cls.set_client()

                print(f"\nAttempting to {func.__name__.replace('_', ' ')}...")
                
                # 1. Call the original method to get the raw API response
                pascal_case_result = func(cls, *args, **kwargs)

                # 2. If the call was successful, convert the keys before returning
                if pascal_case_result is not None:
                    return cls._convert_data_keys(pascal_case_result)
                
                # Return None if the original result was None
                return None

            except EbioseCloudError as e:
                print(f"An API error occurred: {e}")
                if e.response_text:
                    print(f"Raw error response from server: {e.response_text}")
                return None

            except Exception as e:
                print(f"An unexpected error occurred: {e}")
                return None
        return wrapper

    @classmethod
    @_handle_api_errors
    def get_user_id(cls) -> str | None:
        """Get the user ID from the API."""
        response = cls._client.user_info()
        return response.uuid

    @classmethod
    @_handle_api_errors
    def log(cls, message: dict[str, any]) -> None:
        """Log a message to the API."""
        json_message = json.dumps(message, sort_keys=True)
        log_entry = LogEntryInputModel(
             index=ES_INDEX,
             data=json_message,
        )
        cls._client.add_log_entry(data=log_entry)


    @classmethod
    @_handle_api_errors
    def get_ecosystems(cls) -> list | None:
        """Get all ecosystem UUIDs."""
        list_of_ecosystems = cls._client.list_ecosystems()

        if list_of_ecosystems:
            return list_of_ecosystems
        else:
            print("No ecosystems were found.")
            return []

    @classmethod
    @_handle_api_errors
    def get_first_ecosystem_uuid(cls) -> str:
        """Get the first ecosystem UUID."""
        ecosystems = cls.get_ecosystems()
        return ecosystems[0].uuid if ecosystems else None

    @classmethod
    @_handle_api_errors
    def delete_agents(cls, ecosystem_id: str, agent_ids: list[str]) -> None:
        """Delete agents in an ecosystem."""
        if not agent_ids:
            print("No agents to delete.")
            return
        
        print(f"Deleting agents with IDs: {agent_ids} from ecosystem {ecosystem_id}")
        cls._client.delete_agents_from_ecosystem(
            ecosystem_uuid=ecosystem_id, 
            agent_uuids=agent_ids,
        )

    @classmethod
    @_handle_api_errors
    def add_agents_from_forge_cycle(cls, forge_cycle_id: str, agents: list["Agent"]) -> None:
        """Post agents in a forge cycle."""
        
        agents_data = [format_agent(agent) for agent in agents]
        return cls._client.add_agents_during_forge_cycle(
            forge_cycle_uuid=forge_cycle_id, agents_data=agents_data,
        )
    
    @classmethod
    @_handle_api_errors
    def add_agent_from_forge_cycle(
        cls, forge_cycle_id: str, agent: "Agent",
    ) -> None:
        """Post a single agent in a forge cycle."""
        
        agent_data = format_agent(agent)
        agent_output_model = cls._client.add_agent_during_forge_cycle(
            forge_cycle_uuid=forge_cycle_id, data=agent_data,
        )

        return agent_output_model.uuid

    @classmethod
    @_handle_api_errors
    def get_ecosystem(cls, ecosystem_id: str) -> Ecosystem | None:
        """Get an ecosystem by its UUID."""
        # TODO(xabier): we don't need the ecosystem to be loaded from the API,
        # we just need to get architect and genetic operator agents from the API
        # based on the selected agents from the ecosystem.
        response = cls._client.get_ecosystem(uuid=ecosystem_id)
        if response:
            agents = [
                AgentFactory.load_agent_from_api(agent_data)
                for agent_data in response.agents or []
            ]
            # TODO(xabier): understand why this import is agneeded here
            from ebiose.core.agent import Agent
            Ecosystem.model_rebuild()
            return Ecosystem(
                id=response.uuid,
                agents={agent.id: agent for agent in agents},
            )
        else:
            print(f"No ecosystem found with UUID: {ecosystem_id}")
            return None


    @classmethod
    @_handle_api_errors
    def get_agents(cls, ecosystem_id: str) -> list["Agent"] | None:
        response = cls._client.list_agents_in_ecosystem(ecosystem_uuid=ecosystem_id)
        print(f"response: {response}")
        agents = []
        for r in response:
            agent = AgentFactory.load_agent_from_api(r)
            agents.append(agent)
        return agents

    @classmethod
    @_handle_api_errors
    def add_forge(
        cls,
        name: str,
        description:str,
        ecosystem_id: str,
    ) -> str | None:

        forge_input_model = ForgeInputModel(
            name=name,
            description=description,
            ecosystemUuid=ecosystem_id,
        )
        response = cls._client.add_forge(
            data=forge_input_model,
        )
        return response.uuid


    @classmethod
    @_handle_api_errors
    def start_new_forge_cycle(
        cls,
        ecosystem_id: str,
        forge_name: str,
        forge_description: str,
        forge_cycle_config: "CloudForgeCycleConfig",
        override_key: bool | None = None,
    )-> tuple[str, str, str, str]:

        forge_id = cls.add_forge(
            name=forge_name,
            description=forge_description,
            ecosystem_id=ecosystem_id,
        )

        forge_cycle_input = ForgeCycleInputModel(
            nAgentsInPopulation=forge_cycle_config.n_agents_in_population,
            nSelectedAgentsFromEcosystem=forge_cycle_config.n_selected_agents_from_ecosystem,
            nBestAgentsToReturn=forge_cycle_config.n_best_agents_to_return,
            replacementRatio=forge_cycle_config.replacement_ratio,
            tournamentSizeRatio=forge_cycle_config.tournament_size_ratio,
            localResultsPath= None, # forge_cycle_config.local_results_path, no use to send it to the server side
            budget=forge_cycle_config.budget,
        )

        new_cycle_output = cls._client.start_new_forge_cycle(
            forge_uuid=forge_id,
            data=forge_cycle_input, 
            override_key=override_key,
        )

        return new_cycle_output.liteLLMKey, new_cycle_output.baseUrl, new_cycle_output.forgeCycleUuid, forge_id

    @classmethod
    @_handle_api_errors
    def select_agents(cls, ecosystem_id:str, nb_agents:int, forge_cycle_uuid: str) -> list["Agent"]:
        """Select agents from an ecosystem."""
        # TODO(xabier): remove unused parameter ecosystem_id
        response = cls._client.select_agents_for_forge_cycle(
            forge_cycle_uuid=forge_cycle_uuid,
            nb_agents= 100, # nb_agents, # TODO(xabier): fix when server side is ready (then should at least filter on agent_type==None)
        )
        agents = []
        for r in response:
            agent = AgentFactory.load_agent_from_api(r)
            if agent.agent_type is None:  # Filter out architect and genetic operator agents
                agents.append(agent)

        # TODO(xabier): random choice should be handled server-side
        return random.choices(agents, k=nb_agents) if len(agents) >= nb_agents else agents
    
    @classmethod
    @_handle_api_errors
    def get_cost(cls, forge_cycle_uuid: str) -> float:
        return cls._client.get_spend(forge_cycle_uuid=forge_cycle_uuid)
    
    @classmethod
    @_handle_api_errors
    def end_forge_cycle(
        cls,
        forge_cycle_uuid: str,
        winning_agents: list["Agent"],
    ) -> None:
        """End a forge cycle."""
        agents_data = [
            build_agent_input_model(agent) for agent in winning_agents
        ]
        cls._client.end_forge_cycle(
            forge_cycle_uuid=forge_cycle_uuid,
            agents_data=agents_data,
        )

def get_sample_agent() -> "Agent":
    from pydantic import BaseModel, Field, ConfigDict
    from ebiose.core.agent import Agent

    class AgentInput(BaseModel):
        math_problem: str = Field(..., description="The mathematical word problem to solve")

    class AgentOutput(BaseModel):
        """The expected final output to the mathematical problem."""
        #   rationale: str = Field(..., description="The rationale for the solution")
        solution: int = Field(..., description="The solution to the problem.")

    shared_context_prompt = """
    Your are part of a multi-node agent that solves math problems.
    The agent has two main nodes: the solver node and the verifier node.
    The solver node solves the math problem and the verifier node verifies the solution
    given by the solver node. If it is incorrect, the verifier node provides insights
    back to the solver node so that it improves the solution.
    """

    from ebiose.core.engines.graph_engine.nodes import LLMNode

    solver_prompt = """
    Your are the Solver node. You must solve the given math problem.
    """

    solver_node = LLMNode(
        id="solver",
        name="Solver",
        purpose="solve the math problem",
        prompt=solver_prompt,
    )
    verifier_prompt = """
    You are the Verified node.
    Based on the solution provided by the Solver node,
    you must decide whether the solution is correct or not.
    If the solution is incorrect, explain why and provide insights back
    to the solver node so that it improves the solution.
    """

    verifier_node = LLMNode(
        id="verifier",
        name="Verifier",
        purpose="verify the math problem",
        prompt=verifier_prompt,
    )

    from ebiose.core.engines.graph_engine.nodes import StartNode, EndNode

    start_node = StartNode()
    end_node = EndNode()

    from ebiose.core.engines.graph_engine.graph import Graph
    from ebiose.core.engines.graph_engine.edge import Edge

    math_graph = Graph(shared_context_prompt=shared_context_prompt)

    # adding nodes
    math_graph.add_node(start_node)
    math_graph.add_node(solver_node)
    math_graph.add_node(verifier_node)
    math_graph.add_node(end_node)

    # adding edges
    # from start to solver
    math_graph.add_edge(Edge(start_node_id=start_node.id, end_node_id=solver_node.id))
    # from solver to verifier
    math_graph.add_edge(Edge(start_node_id=solver_node.id, end_node_id=verifier_node.id))
    # from verifier to end,  if the condition is correct
    math_graph.add_edge(Edge(start_node_id=verifier_node.id, end_node_id=end_node.id, condition="correct"))
    # from verifier to solver, if the condition is incorrect
    math_graph.add_edge(Edge(start_node_id=verifier_node.id, end_node_id=solver_node.id, condition="incorrect"))

    from ebiose.core.agent_engine_factory import AgentEngineFactory


    math_graph_engine = AgentEngineFactory.create_engine(
        engine_type="langgraph_engine",
        agent_id = "agent-" + str(uuid.uuid4()),
        configuration={
            "graph": math_graph.model_dump(),
            "input_model": AgentInput.model_json_schema(),
            "output_model": AgentOutput.model_json_schema(),
        },
        # input_model=AgentInput,
        # output_model=AgentOutput,
        model_endpoint_id="azure/gpt-4o-mini"
    )
    
    # TODO(xabier): handle model_endpoint_id independently of the agent engine
    architect_agent = GraphUtils.get_architect_agent(model_endpoint_id="azure/gpt-4o-mini")
    crossover_agent = GraphUtils.get_crossover_agent(model_endpoint_id="azure/gpt-4o-mini")
    mutation_agent = GraphUtils.get_mutation_agent(model_endpoint_id="azure/gpt-4o-mini")

    return Agent(
        name="Math Agent",
        description="An agent that solves math problems",
        agent_engine=math_graph_engine,
        id = math_graph_engine.agent_id,
        architect_agent_id=architect_agent.id,
        genetic_operator_agent_id=crossover_agent.id,
    )
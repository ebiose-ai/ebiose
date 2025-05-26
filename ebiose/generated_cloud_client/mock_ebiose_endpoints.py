
from typing import TYPE_CHECKING
import uuid

from ebiose.core.engines.graph_engine.utils import GraphUtils
from ebiose.core.model_endpoint import ModelEndpoints
from ebiose.generated_cloud_client.models.agent_engine_input_model import AgentEngineInputModel
if TYPE_CHECKING:
    from ebiose.core.forge_cycle import ForgeCycleConfig

from ebiose.core.agent import Agent
from uuid import uuid4

from ebiose.generated_cloud_client.client import Client
from ebiose.generated_cloud_client.api.forge_cycle_endpoints import start_new_forge_cycle
from ebiose.generated_cloud_client.models.forge_cycle_input_model import ForgeCycleInputModel
from ebiose.generated_cloud_client.api.ecosystem_endpoints import get_ecosystems_ecosystem_uuid_agents, get_ecosystems_ecosystem_uuid_select_agents 
from ebiose.generated_cloud_client.api.ecosystem_endpoints import get_ecosystems
from ebiose.generated_cloud_client.api.ecosystem_endpoints import post_ecosystems_ecosystem_uuid_agents
from ebiose.generated_cloud_client.models.agent_input_model import AgentInputModel
from ebiose.generated_cloud_client.api.forge_cycle_endpoints import end_forge_cycle
# from ebiose.core.model_endpoint import ModelEndpoints

STATUS_OK = 200


# def check_ebiose_api_key() -> bool:
#     # check user authentication 
#     api_key = ModelEndpoints.get_ebiose_api_key()
#     if api_key is None:
#         msg = "No Ebiose API key found. Please set the Ebiose API key "
#         msg += "or use the local forge cycle mode instead."
#         raise ValueError(msg)

#     return api_key == "sk-ebiose-test-key"

# def get_ecosystem() -> Ecosystem:
#     # retrieve the ecosystem object from the user
#     return 


def build_agent_input_model(agent: Agent) -> AgentInputModel:
    """Build the AgentInputModel from the Agent."""
    agent_engine_input_model = AgentEngineInputModel(
        engine_type=agent.agent_engine.engine_type,
        configuration=agent.agent_engine.model_dump_json(),
    )
    return AgentInputModel(
        # uuid=agent.id, # TODO(gildas): add this field to the server side
        name=agent.name,
        description=agent.description,
        agent_engine=agent_engine_input_model,
        architect_agent_uuid=agent.architect_agent.id if agent.architect_agent else None,
        genetic_operator_agent_uuid=agent.genetic_operator_agent.id if agent.genetic_operator_agent else None,
        description_embedding=None,
        # description_embedding=agent.description_embedding, # TODO(gildas): add this field as list of float to the server side
    )


class EbioseAPIClient:
    _client: Client | None = None

    @classmethod
    def set_client(cls) -> None:
        """Set the API client with the provided API key."""
        if cls._client is None:
            cls._client = Client(
                base_url=ModelEndpoints.get_ebiose_api_base(),
                headers={"ApiKey": ModelEndpoints.get_ebiose_api_key()},
            )


    @classmethod
    def post_agents(cls, agents: list[Agent], ecosystem_id: str) -> None:
        """Add agents to an ecosystem."""
        if cls._client is None:
            cls.set_client()
        body = [build_agent_input_model(agent) for agent in agents]        

        response = post_ecosystems_ecosystem_uuid_agents.sync_detailed(
            ecosystem_uuid=ecosystem_id, client=cls._client, body=body,
        )
        if response.status_code == STATUS_OK:
            return response.parsed
        else:
            raise Exception(f"Error adding agents: {response.status_code} - {response.content}")


    @classmethod
    def get_agents(cls, ecosystem_id: str) -> list[Agent]:
        """Get all agents in an ecosystem."""
        if cls._client is None:
            cls.set_client()

        response = get_ecosystems_ecosystem_uuid_agents.sync_detailed(
            client=cls._client,
            ecosystem_uuid=ecosystem_id,
        )
        if response.status_code == STATUS_OK:
            return response.parsed
        else:
            raise Exception(f"Error getting agents: {response.status_code} - {response.content}")
    @classmethod
    def start_new_forge_cycle(
        cls,
        forge_name: str,
        forge_description: str,
        forge_cycle_config: "ForgeCycleConfig",
    ) -> tuple[str, str]:
        """Start a new forge cycle and return the lite_llm_api_key and forge_cycle_id."""
        if cls._client is None:
            cls.set_client()

        forge_cycle_input_model = ForgeCycleInputModel(
            forge_name=forge_name,
            forge_description=forge_description,
            n_agents_in_population=forge_cycle_config.n_agents_in_population,
            n_selected_agents_from_ecosystem=forge_cycle_config.n_selected_agents_from_ecosystem,
            n_best_agents_to_return=forge_cycle_config.n_best_agents_to_return,
            replacement_ratio=forge_cycle_config.replacement_ratio,
            tournament_size_ratio=forge_cycle_config.tournament_size_ratio,
            local_results_path=forge_cycle_config.local_results_path,
            budget=forge_cycle_config.budget,
        )

        response = start_new_forge_cycle.sync_detailed(client=cls._client, body=forge_cycle_input_model)
        if response.status_code == STATUS_OK:
            lite_llm_api_key = response.parsed.lite_llm_key
            forge_cycle_id = response.parsed.forge_cycle_uuid
            return lite_llm_api_key, forge_cycle_id
        else:
            raise Exception(f"Error starting new forge cycle: {response.status_code} - {response.content}")


    @classmethod
    def get_ecosystem_uuid(cls) -> str:
        """Get the ecosystem UUID."""
        if cls._client is None:
            cls.set_client()

        response = get_ecosystems.sync_detailed(client=cls._client)
        if response.status_code == STATUS_OK:
            # TODO(xabier): fix for multiple existing ecosystems
            return response.parsed[0].uuid
        else:
            raise Exception(f"Error getting ecosystem UUID: {response.status_code} - {response.content}")

    @classmethod
    def select_agents(
        cls,
        forge_description: str,
        n_selected_agents: int = 1, # should be capped to some number on the server side
    ) -> list[Agent]:
        ecosystem_uuid = cls.get_ecosystem_uuid()
        response = get_ecosystems_ecosystem_uuid_select_agents.sync_detailed(
            client=cls._client,
            ecosystem_uuid=ecosystem_uuid,
            nb_agents=n_selected_agents,
            forge_description=forge_description,
        )
        if response.status_code == STATUS_OK:
            selected_agents = response.parsed
            # TODO(xabier): fix for multiple existing ecosystems
            # TODO(xabier): check if the agent is already in the ecosystem.
            # if so, it should be copied with a new id and full metabolism
            return selected_agents
        else:
            raise Exception(f"Error selecting agents: {response.status_code} - {response.content}")

    @classmethod
    def end_forge_cycle(
        cls,
        forge_cycle_id: str,
        winning_agents: list[Agent], # should create new agents server side with full metabolism
        # (must double check if the agent is already in the ecosystem.
        # if so, it should be copied with a new id and full metabolism)
        # agent_metabolism_updates: dict[str, float], # {"agent-...": 0.5, ...}
        # selected_agents: list[Agent], # should update their metabolism server side         
        agent_metabolism_updates: dict[str, float], # {"agent-...": 0.5, ...}
    ):
        # called at the end of a forge cycle (or whenever an error is raised )
        # deletes the lite_llm_api_key but keep the forge cycle id
        response = end_forge_cycle.sync_detailed(
            client=cls._client,
            forge_cycle_uuid=forge_cycle_id,
        )
        if response.status_code == STATUS_OK:
            return response.parsed
        else:
            raise Exception(f"Error ending forge cycle: {response.status_code} - {response.content}")
        


def select_agents(
        forge_cycle_id: str,
        n_selected_agents: int = 1, # should be capped to some number on the server side
    ) -> list[Agent]:
    
    # agent.forge_history = ["math forge", "physic forge"]
    selected_agents = [get_sample_agent() for _ in range(n_selected_agents)]
    return selected_agents


def end_forge_cycle(
        forge_cycle_id: str,
        winning_agents: list[Agent], # should create new agents server side with full metabolism
        # (must double check if the agent is already in the ecosystem.
        # if so, it should be copied with a new id and full metabolism)
        agent_metabolism_updates: dict[str, float], # {"agent-...": 0.5, ...}
        # selected_agents: list[Agent], # should update their metabolism server side         
    ):
    # called at the end of a forge cycle (or whenever an error is raised )
    # deletes the lite_llm_api_key but keep the forge cycle id
    pass

def get_spent_budget(forge_cycle_id: str) -> float:
    # returns the spent budget so far
    pass

def get_sample_agent() -> Agent:
    from pydantic import BaseModel, Field, ConfigDict

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
        architect_agent=architect_agent,
        genetic_operator_agent=mutation_agent,
    )
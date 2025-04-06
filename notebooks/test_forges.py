import asyncio
from pydantic import BaseModel
from ebiose.compute_intensive_batch_processor.compute_intensive_batch_processor import ComputeIntensiveBatchProcessor
from ebiose.core.agent import Agent
from ebiose.core.agent_factory import AgentFactory
from ebiose.core.agent_forge import AgentForge
from ebiose.backends.langgraph.engine.utils import GraphUtils




async def generate_agents(
    forge_description: str,
    agent_input_model: type[BaseModel],
    agent_output_model: type[BaseModel],
    model_endpoint_id: str,
    n_agents: int,
):

    # Generate agents using the architect agent
    architect_agent = GraphUtils.get_architect_agent(
        model_endpoint_id=model_endpoint_id,
    )

    architect_agent_input = architect_agent.agent_engine.input_model(
        forge_description = forge_description,
        # node_types = ["StartNode", "LLMNode", "EndNode"],
        node_types = [
            "StartNode", 
            "LLMNode", 
            "EndNode",
            "PythonNode",
            "DatabaseNode",
            "APINode",
            "WebScraperNode",
            "FileNode",
            "UserQueryNode",
        ],
        max_llm_nodes = 10,
        random_n_llm_nodes = True,
    )

    ComputeIntensiveBatchProcessor.initialize()
    master_compute_token = ComputeIntensiveBatchProcessor.acquire_master_token(budget=10)
    architect_agent_compute_token = ComputeIntensiveBatchProcessor.generate_token(
        10,
        master_compute_token,
    )

    architect_agent_tasks = []
    for _ in range(n_agents):
        result = AgentFactory.generate_agent(
            architect_agent=architect_agent,
            agent_input=architect_agent_input,
            compute_token_id=architect_agent_compute_token,
            genetic_operator_agent=None,
            generated_agent_engine_type="langgraph_engine",
            generated_model_endpoint_id=MODEL_ENDPOINT_ID,
            generated_agent_input=agent_input_model,
            generated_agent_output=agent_output_model,
        )
        
        architect_agent_tasks.append(result)

    return await asyncio.gather(*architect_agent_tasks)


if __name__ == "__main__":
    forge_description = "Solving math problem"
    forge_description = "Mangaging the tickets incoming to the system and assigning them to the right agent. The system is a ticketing system for a company that sells tickets for events. The system has a lot of different types of tickets, and the agents are responsible for managing the tickets and assigning them to the right people. The system has a lot of different types of tickets, and the agents are responsible for managing the tickets and assigning them to the right people. The system has a lot of different types of tickets, and the agents are responsible for managing the tickets and assigning them to the right people."
    forge_description = "organize a trip in a given destination."
    class AgentInput(BaseModel):
        math_problem: str

    class AgentOutput(BaseModel):
        solution: int
        rationale: str

    MODEL_ENDPOINT_ID = "azure-gpt-4o-mini"
    N_AGENTS = 2

    results = asyncio.run(
         generate_agents(
            forge_description=forge_description,
            agent_input_model=AgentInput,
            agent_output_model=AgentOutput,
            model_endpoint_id=MODEL_ENDPOINT_ID,
            n_agents=N_AGENTS,
        )
    )

    for i, result in enumerate(results):
        print(f"Agent {i} generated:")
        if result is not None:
            print(result.agent_engine.graph.to_mermaid_str(orientation="TD"))
            for node in result.agent_engine.graph.nodes:
                if node.type == "LLMNode":
                    print(f"Node ID: {node.id}, Prompt: {node.prompt}")
        else:
            print("Failed to generate agent.")

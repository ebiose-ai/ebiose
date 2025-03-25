
from ebiose.backends.langgraph.engine.base_agents.architect_agent import init_architect_agent
from ebiose.backends.langgraph.engine.base_agents.crossover_agent import init_crossover_agent
from ebiose.core.model_endpoint import ModelEndpoints
from ebiose.generated_cloud_client.mock_ebiose_endpoints import EbioseAPIClient
from ebiose.generated_cloud_client.mock_ebiose_endpoints import get_sample_agent


ebiose_client = EbioseAPIClient()

ecosystem_uuid = ebiose_client.get_first_ecosystem_uuid()
print(f"ecosystem_uuid: {ecosystem_uuid}")

# getting all agents in the ecosystem
if False:
    response = ebiose_client.get_agents(ecosystem_id=ecosystem_uuid)
    print(f"response: {response}")

# adding architect agent to the ecosystem
architect_agent = init_architect_agent(
    model_endpoint_id=ModelEndpoints.get_default_model_endpoint_id(),
    add_format_node=True,
)

architect_test_id = "test-architect-agent2"
architect_agent.id = architect_test_id
architect_agent.agent_engine.agent_id = architect_test_id

if False:
    response = ebiose_client.add_agents(
        agents=[architect_agent],
        ecosystem_id=ecosystem_uuid,
    )
    print(f"response: {response}")


crossover_test_id = "test-crossover-agent3"
crossover_agent = init_crossover_agent(
    model_endpoint_id=ModelEndpoints.get_default_model_endpoint_id(),
)
crossover_agent.id = crossover_test_id
crossover_agent.agent_engine.agent_id = crossover_test_id
if True:
    response = ebiose_client.add_agents(
        agents=[crossover_agent],
        ecosystem_id=ecosystem_uuid,
    )
    print(f"response: {response}")




# adding an agent to the ecosystem
if True:
    agent = get_sample_agent()
    print(f"agent: {agent}")
    agent.id = "test-agent-4"
    agent.agent_engine.agent_id = agent.id
    agent.architect_agent = architect_agent
    agent.genetic_operator_agent = crossover_agent

    response = ebiose_client.add_agents(
        agents=[agent],
        ecosystem_id=ecosystem_uuid,
    )

    print(f"response: {response}")

# trying to reload the posted agent
agents = ebiose_client.get_agents(ecosystem_id=ecosystem_uuid)

print(f"agents: {agents}")

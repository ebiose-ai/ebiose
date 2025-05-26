
from ebiose.backends.langgraph.engine.base_agents.architect_agent import init_architect_agent
from ebiose.core.model_endpoint import ModelEndpoints
from ebiose.generated_cloud_client.mock_ebiose_endpoints import EbioseAPIClient
from ebiose.generated_cloud_client.mock_ebiose_endpoints import get_sample_agent

ebiose_client = EbioseAPIClient()

ecosystem_uuid = ebiose_client.get_ecosystem_uuid()
print(f"ecosystem_uuid: {ecosystem_uuid}")

# getting all agents in the ecosystem
response = ebiose_client.get_agents(ecosystem_id=ecosystem_uuid)
print(f"response: {response}")

# adding architect agent to the ecosystem
architect_agent = init_architect_agent(
    model_endpoint_id=ModelEndpoints.get_default_model_endpoint_id(),
    add_format_node=True,
)

response = ebiose_client.post_agents(
    agents=[architect_agent],
    ecosystem_id=ecosystem_uuid,
)

print(f"response: {response}")

# adding an agent to the ecosystem
# agent = get_sample_agent()
# print(f"agent: {agent}")

# response = ebiose_client.post_agents(
#     agents=[agent],
#     ecosystem_id=ecosystem_uuid,
# )

# print(f"response: {response}")
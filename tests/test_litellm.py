from langchain_openai import ChatOpenAI
import litellm

from ebiose.cloud_client.ebiose_api_client import EbioseAPIClient
from ebiose.core.forge_cycle import CloudForgeCycleConfig

# Get an API key from Ebiose API client
ecosystem_id = EbioseAPIClient.get_first_ecosystem_uuid()  
forge_cycle_config = CloudForgeCycleConfig(
    mode="cloud", budget=1.0,
)
# forge_id = EbioseAPIClient.add_forge(
#     ecosystem_id=ecosystem_id,
#     forge_name="Test Forge",
#     forge_description="",
#     forge_cycle_config=forge_cycle_config,
# )
litellm._turn_on_debug()    
litellm_api_key, litellm_api_base, forge_cycle_id, forge_id = EbioseAPIClient.start_new_forge_cycle(
    ecosystem_id=ecosystem_id,
    forge_name="Test Forge",
    forge_description="some forge",
    forge_cycle_config=forge_cycle_config,
    override_key=True,
)

response = ChatOpenAI(
    openai_api_key=litellm_api_key,
    openai_api_base=litellm_api_base,
    model="azure/gpt-4o-mini",
    temperature=0.7,
    max_tokens=2**15,
).ainvoke(
    [{"role": "user", "content": "Hello Proxy!"}],
)
response = litellm.completion(
    model="azure/gpt-4o-mini",                  # must match your proxy's config
    messages=[{"role": "user", "content": "Hello Proxy!"}],
    api_base=litellm_api_base,     # your LiteLLM Proxy URL
    api_key=litellm_api_key,   
    api_version="2024-12-01-preview",  # must match your proxy's config

)

print(response["choices"][0]["message"]["content"])

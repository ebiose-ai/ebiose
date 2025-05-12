from langchain_openai import AzureChatOpenAI
from ebiose.core.model_endpoint import ModelEndpoints

model_endpoint = ModelEndpoints.get_model_endpoint("azure-gpt-4o-mini")

llm = AzureChatOpenAI(
    azure_deployment=model_endpoint.deployment_name,
    azure_endpoint=model_endpoint.endpoint_url.get_secret_value(),
    openai_api_key=model_endpoint.api_key.get_secret_value(),
    openai_api_version=model_endpoint.api_version,
    max_tokens=512,
    temperature=0.3,
    request_timeout=10
)

prompt = (
    "If Sarah has 3 apples and buys 4 more, then gives 2 to her friend, "
    "how many apples does she have left?"
)

response = llm.invoke(prompt)

print("\n=== Model Response ===\n")
print(response.content)
print("\n======================\n")

from langchain_openai import AzureChatOpenAI
from ebiose.core.model_endpoint import ModelEndpoints

model_endpoint = ModelEndpoints.get_model_endpoint("azure-gpt-4o-mini")

llm = AzureChatOpenAI(
    azure_deployment=model_endpoint.deployment_name,
    azure_endpoint=model_endpoint.endpoint_url.get_secret_value(),
    openai_api_key=model_endpoint.api_key.get_secret_value(),
    openai_api_version=model_endpoint.api_version,
    max_tokens=1,
    temperature=0,
    request_timeout=5
)

response = llm.invoke("Hi")
print(response)

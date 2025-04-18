
from langchain_community.chat_models import ChatLiteLLM
from langchain_core.messages import HumanMessage
from ebiose.core.model_endpoint import ModelEndpoints

import asyncio
import nest_asyncio
nest_asyncio.apply()
from ebiose.core.engines.graph_engine.nodes import LLMNode
from ebiose.core.engines.graph_engine.nodes import StartNode, EndNode
from ebiose.core.engines.graph_engine.graph import Graph
from ebiose.core.engines.graph_engine.edge import Edge

from pydantic import BaseModel, Field, ConfigDict
import litellm
litellm.success_callback = ["langfuse"]
litellm.failure_callback = ["langfuse"]

model_endpoint_id = "azure-gpt-4o-mini"
model_endpoint = ModelEndpoints.get_model_endpoint(model_endpoint_id)

if False:

    chat = ChatLiteLLM(
        model="azure/gpt-4o-mini",
        azure_api_key=model_endpoint.api_key.get_secret_value(),
        api_base=model_endpoint.endpoint_url.get_secret_value(),
        temperature=0.7,
        request_timeout=60,
        max_retries=3,
        max_tokens=4000,
        model_kwargs={
                        "metadata": {
                            "trace_user_id": "user-id", # set Langfuse Trace User ID
                            "session_id": "session-id", # set Langfuse Session ID
                            "tags": ["tag1", "tag2"] # set Langfuse Tags
                    },
                    }
    ).bind_tools(tools=[]).with_retry(
                    wait_exponential_jitter=True,
                    stop_after_attempt=10,
                )
    messages = [
        HumanMessage(
            content="Translate this sentence from English to French. I love programming."
        )
    ]

    chat_call = asyncio.run(chat.ainvoke(messages))

    print(chat_call)

if True:
        

    class AgentInput(BaseModel):
        math_problem: str = Field(..., description="The mathematical word problem to solve")

    class AgentOutput(BaseModel):
        """The expected final output to the mathematical problem."""
        rationale: str = Field(..., description="The rationale for the solution")
        solution: int = Field(..., description="The solution to the problem.")

    shared_context_prompt = """
    Your are part of a multi-node agent that solves math problems.
    The agent has two main nodes: the solver node and the verifier node.
    The solver node solves the math problem and the verifier node verifies the solution
    given by the solver node. If it is incorrect, the verifier node provides insights
    back to the solver node so that it improves the solution.
    """

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


    start_node = StartNode()
    end_node = EndNode()



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


    from pprint import pprint
    from ebiose.core.agent import Agent
    from ebiose.core.agent_engine_factory import AgentEngineFactory

    math_graph_engine = AgentEngineFactory.create_engine(
        engine_type="langgraph_engine",
        configuration={"graph": math_graph.model_dump()},
        input_model=AgentInput,
        output_model=AgentOutput,
        model_endpoint_id="azure-gpt-4o-mini"
    )

    math_agent = Agent(
        name="Math Agent",
        description="An agent that solves math problems",
        agent_engine=math_graph_engine,
    )

    # pprint(math_agent.model_dump())

    agent_input = math_agent.agent_engine.input_model(
        math_problem="Natalia sold clips to 48 of her friends in April, and then she sold half as many clips in May. How many clips did Natalia sell altogether in April and May?"
    )
    # we could have also used AgentInput(math_problem=...) as well

    from ebiose.compute_intensive_batch_processor.compute_intensive_batch_processor import ComputeIntensiveBatchProcessor
    from ebiose.core.model_endpoint import ModelEndpoint

    ComputeIntensiveBatchProcessor.initialize()
    BUDGET = 0.01

    import asyncio
    import nest_asyncio
    nest_asyncio.apply()
    response = asyncio.run(math_agent.run(agent_input))
    pprint(response)

if False:
    from langgraph.graph import StateGraph, START, END
    from langchain_community.chat_models import ChatLiteLLM
    from langchain_core.messages import HumanMessage, AIMessage
    from typing import TypedDict, List

    # Define the state
    class AgentState(TypedDict):
        messages: List[HumanMessage | AIMessage]

    # Create the LiteLLM model
    llm = ChatLiteLLM(
        model="azure/gpt-4o-mini",
        azure_api_key=model_endpoint.api_key.get_secret_value(),
        api_base=model_endpoint.endpoint_url.get_secret_value(),
    )

    # Define the node function that calls the LLM
    async def call_llm(state: AgentState):
        # Get the latest message
        messages = state['messages']
        
        # Call the LLM
        response = await llm.ainvoke(messages)
        
        # Return the updated state with the new AI message
        return {"messages": [response]}

    # Create the graph
    workflow = StateGraph(AgentState)

    # Add the LLM node
    workflow.add_node("llm", call_llm)

    # Set the entry point
    workflow.add_edge(START, "llm")

    # End the graph after the LLM call
    workflow.add_edge("llm", END)

    # Compile the graph
    agent = workflow.compile()

    # Example usage
    initial_messages = [HumanMessage(content="Tell me a short joke")]
    result = asyncio.run(agent.ainvoke({"messages": initial_messages}))



    # Print the result
    for message in result['messages']:
        print(message.content)
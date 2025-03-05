import asyncio
import json
from datetime import UTC, datetime
from pathlib import Path

from dotenv import load_dotenv
from loguru import logger

from ebiose.compute_intensive_batch_processor.compute_intensive_batch_processor import (
    ComputeIntensiveBatchProcessor,
)
from ebiose.core.agent_factory import AgentFactory
from examples.math_forge.math_forge import MathLangGraphForge

load_dotenv()


TRAIN_CSV_PATH = "./examples/math_forge/gsm8k_train.csv" # the train dataset
TEST_CSV_PATH = "./examples/math_forge/gsm8k_test.csv" # the test dataset
AGENT_JSON_FILE = Path("data/2025-02-28_17-49-05/generation=2/agents/agent-211c7fe5-d329-470e-bdd9-ae7ee6ce0be3.json")
N_PROBLEMS = 2 # number of problems to evaluate on
BUDGET = 0.1 # budget for evaluation in dollars

# instantiating the forge
forge = MathLangGraphForge(
    train_csv_path=TRAIN_CSV_PATH,
    test_csv_path=TEST_CSV_PATH,
    n_problems=N_PROBLEMS,
)

# loading agent
with Path.open(AGENT_JSON_FILE) as json_file:
    agent_configuration = json.load(json_file)

agent = AgentFactory.load_agent(
    agent_config=agent_configuration,
    model_endpoint_id="azure-gpt-4o-mini",
    input_model=forge.agent_input_model,
    output_model=forge.agent_output_model,
)

# generating the compute token
ComputeIntensiveBatchProcessor.initialize()
master_token_id = ComputeIntensiveBatchProcessor.acquire_master_token(BUDGET)
compute_token_id = ComputeIntensiveBatchProcessor.generate_token(BUDGET, master_token_id)

# running evaluation on test set
t0 = datetime.now(UTC)
fitness = asyncio.run(
    forge.compute_fitness(
        agent=agent,
        compute_token_id=compute_token_id,
        mode="test",
    ),
)

# getting cost
cost = ComputeIntensiveBatchProcessor.get_token_cost(compute_token_id)

logger.info(f"Evaluation of agent {agent.id} on test set took {datetime.now(UTC) - t0}")
logger.info(f"Computed fitness is: {fitness}, for cost: {cost} $")

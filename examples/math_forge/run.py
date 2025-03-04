import asyncio
import sys
from datetime import UTC, datetime
from pathlib import Path

from dotenv import load_dotenv
from loguru import logger

from ebiose.compute_intensive_batch_processor.compute_intensive_batch_processor import (
    ComputeIntensiveBatchProcessor,
)
from ebiose.core.ecosystem import Ecosystem
from ebiose.core.engines.graph_engine.utils import GraphUtils
from ebiose.core.evo_forging_cycle import EvoForgingCylceConfig
from ebiose.core.model_endpoint import ModelEndpoint, ModelEndpoints
from examples.math_forge.math_forge import MathLangGraphForge
import os
from langfuse.callback import CallbackHandler

langfuse_handler = CallbackHandler(
    secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
    public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
    host=os.getenv("LANGFUSE_HOST"),
)
load_dotenv()

# the path where results will be saved
timestamp = datetime.now(tz=UTC).strftime("%Y-%m-%d_%H-%M-%S")
SAVE_PATH = Path(f"./data/{timestamp}/")
if not SAVE_PATH.exists():
    SAVE_PATH.mkdir(parents=True)



logger.remove()
logger.add(sys.stderr, level="DEBUG")
logger.add(SAVE_PATH / "all_logs.log", rotation="10 MB", level="DEBUG")


ComputeIntensiveBatchProcessor.initialize(ModelEndpoints.get_all_model_endpoints())

architect_agent = GraphUtils.get_architect_agent(model_endpoint_id="azure-gpt-4o-mini")
crossover_agent = GraphUtils.get_crossover_agent(model_endpoint_id="azure-gpt-4o-mini")

eco = Ecosystem(
    initial_architect_agents=[architect_agent],
    initial_genetic_operator_agents=[crossover_agent],
)

N_PROBLEMS = 2 # number of problems to evaluate on, per generation
TRAIN_CSV_PATH = "./examples/math_forge/gsm8k_train.csv" # the train dataset
TEST_CSV_PATH = "./examples/math_forge/gsm8k_test.csv" # the test dataset

forge = MathLangGraphForge(
    train_csv_path=TRAIN_CSV_PATH,
    test_csv_path=TEST_CSV_PATH,
    n_problems=N_PROBLEMS,
)

cycle_config = EvoForgingCylceConfig(
    budget=0.05,
    n_agents_in_population=2,
    n_selected_agents_from_ecosystem=0,
    replacement_ratio=0.5,
    save_path=SAVE_PATH,
)

best_agents, best_finess = asyncio.run(forge.run_new_cycle(eco, cycle_config=cycle_config))

logger.info("Best agents and their fitness:")
forge.display_results(best_agents, best_finess)


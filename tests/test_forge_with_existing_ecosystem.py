"""Copyright (c) 2024, Inria.

Pre-release Version - DO NOT DISTRIBUTE
This software is licensed under the MIT License. See LICENSE for details.
"""

import asyncio
import random
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv
# from loguru import logger
from pydantic import BaseModel

from ebiose.core.agent import Agent
from ebiose.core.agent_forge import AgentForge
from ebiose.core.forge_cycle import CloudForgeCycleConfig, LocalForgeCycleConfig



 # loading dotenv
load_dotenv()


# the path where results will be saved
timestamp = datetime.now(tz=UTC).strftime("%Y-%m-%d_%H-%M-%S")
SAVE_PATH = Path(f"./data/{timestamp}/")
if not SAVE_PATH.exists():
    SAVE_PATH.mkdir(parents=True)

# logging config
# logger.remove()
# logger.add(sys.stderr, level="DEBUG")


# run parameters
BUDGET = 0.02 # budget in dollars
N_PROBLEMS = 1 # number of problems to evaluate on, per generation
TRAIN_CSV_PATH = "./examples/math_forge/gsm8k_train.csv" # the train dataset
TEST_CSV_PATH = "./examples/math_forge/gsm8k_test.csv" # the test dataset
DEFAULT_MODEL_ENDPOINT_ID = None # set if you want to use a specific model endpoint for generated agents
PROBLEM_DESCRIPTION = "Solve word math problems"
MODE = "cloud"

# defining the forge
class AgentInput(BaseModel):
    math_problem: str

class AgentOutput(BaseModel):
    solution: int
    rationale: str

class MathForge(AgentForge):
    name: str = "Math Forge"
    description: str = PROBLEM_DESCRIPTION

    agent_input_model: type[BaseModel] = AgentInput
    agent_output_model: type[BaseModel] = AgentOutput
    default_generated_agent_engine_type: str = "langgraph_engine"

    async def compute_fitness(self, agent: Agent, mode: Literal["train", "test"] = "train", **kwargs: dict[str, any]) -> float:
        return random.random()


# running the forge cycle
forge = MathForge()

if MODE == "cloud":
    cycle_config = CloudForgeCycleConfig(
        budget=BUDGET,
        n_agents_in_population=2,
        n_selected_agents_from_ecosystem=1,
        n_best_agents_to_return=2,
        replacement_ratio=0.5,
        save_path=SAVE_PATH,
        node_types=["StartNode", "EndNode", "LLMNode"],
    )
elif MODE == "local":
    cycle_config = LocalForgeCycleConfig(
        n_generations = 1,
        n_agents_in_population=2,
        n_selected_agents_from_ecosystem=0,
        n_best_agents_to_return=2,
        replacement_ratio=0.5,
        save_path=SAVE_PATH,
        node_types=["StartNode", "EndNode", "LLMNode" ],
    )

best_agents, best_finess = asyncio.run(
    forge.run_new_cycle(config=cycle_config),
)

# logger.info("Best agents and their fitness:")
forge.display_results(best_agents, best_finess)

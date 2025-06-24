"""Copyright (c) 2024, Inria.

Pre-release Version - DO NOT DISTRIBUTE
This software is licensed under the MIT License. See LICENSE for details.
"""

import asyncio
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal

from loguru import logger

from ebiose.backends.langgraph.llm_api import LangGraphLLMApi
from ebiose.llm_api.llm_api import (
    LLMApi,
)
from ebiose.core.agent_factory import AgentFactory
from examples.math_forge.math_forge import MathLangGraphForge


def main(
    train_csv_path: str,
    test_csv_path: str,
    agent_json_file: str,
    n_problems: int,
    model_endpoint_id: str,
    mode: Literal["local", "cloud"] = "cloud",
) -> None:

    # instantiating the forge
    forge = MathLangGraphForge(
        train_csv_path=train_csv_path,
        test_csv_path=test_csv_path,
        n_problems=n_problems,
        default_model_endpoint_id=model_endpoint_id,
    )

    # loading agent
    with Path.open(agent_json_file) as json_file:
        agent_configuration = json.load(json_file)

    agent = AgentFactory.load_agent(
        agent_config=agent_configuration,
        model_endpoint_id=model_endpoint_id,
    )

    # generating the compute token
    LangGraphLLMApi.initialize(mode=mode)
    
    # running evaluation on test set
    t0 = datetime.now(UTC)
    fitness = asyncio.run(
        forge.compute_fitness(
            agent=agent,
            mode="test",
        ),
    )

    # getting cost
    cost = LangGraphLLMApi.get_total_cost()

    logger.info(f"Evaluation of agent {agent.id} on test set took {datetime.now(UTC) - t0}")
    logger.info(f"Computed fitness is: {fitness}, for cost: {cost} $")


if __name__ == "__main__":

    # loading dotenv
    from dotenv import load_dotenv
    load_dotenv()

    # evaluation parameters
    AGENT_JSON_FILE = "data/2025-06-22_13-53-54/generation=1/agents/agent-ff27cdb8-972a-4e4e-bd47-533293130919.json"
    TRAIN_CSV_PATH = "./examples/math_forge/gsm8k_train.csv" # the train dataset
    TEST_CSV_PATH = "./examples/math_forge/gsm8k_test.csv" # the test dataset
    N_PROBLEMS = 2 # number of problems to evaluate on
    MODEL_ENDPOINT_ID = "azure/gpt-4o-mini" # model endpoint id

    # running the evaluation
    main(
        train_csv_path=TRAIN_CSV_PATH,
        test_csv_path=TEST_CSV_PATH,
        agent_json_file=AGENT_JSON_FILE,
        n_problems=N_PROBLEMS,
        model_endpoint_id=MODEL_ENDPOINT_ID,
    )
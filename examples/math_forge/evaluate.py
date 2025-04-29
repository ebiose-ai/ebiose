"""Copyright (c) 2024, Inria.

Pre-release Version - DO NOT DISTRIBUTE
This software is licensed under the MIT License. See LICENSE for details.
"""

import asyncio
import json
from datetime import UTC, datetime
from pathlib import Path

from loguru import logger

from ebiose.compute_intensive_batch_processor.compute_intensive_batch_processor import (
    ComputeIntensiveBatchProcessor,
)
from ebiose.core.agent_factory import AgentFactory
from examples.math_forge.math_forge import MathLangGraphForge


def main(
    train_csv_path: str,
    test_csv_path: str,
    agent_json_file: str,
    n_problems: int,
    budget: float,
    model_endpoint_id: str,
) -> None:

    # instantiating the forge
    forge = MathLangGraphForge(
        train_csv_path=train_csv_path,
        test_csv_path=test_csv_path,
        n_problems=n_problems,
    )

    # loading agent
    with Path.open(agent_json_file) as json_file:
        agent_configuration = json.load(json_file)

    agent = AgentFactory.load_agent(
        agent_config=agent_configuration,
        model_endpoint_id=model_endpoint_id,
        input_model=forge.agent_input_model,
        output_model=forge.agent_output_model,
    )

    # generating the compute token
    ComputeIntensiveBatchProcessor.initialize()
    master_token_id = ComputeIntensiveBatchProcessor.acquire_master_token(budget)
    compute_token_id = ComputeIntensiveBatchProcessor.generate_token(budget, master_token_id)

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


if __name__ == "__main__":

    # loading dotenv
    from dotenv import load_dotenv
    load_dotenv()

    # evaluation parameters
    AGENT_JSON_FILE = "data/2025-03-10_11-29-05/generation=4/agents/agent-ba8a9d8f-36bc-44b7-aaaf-be10c821f995.json"
    TRAIN_CSV_PATH = "../math_forge/gsm8k_train.csv" # the train dataset
    TEST_CSV_PATH = "../math_forge/gsm8k_train.csv" # the test dataset
    N_PROBLEMS = 2 # number of problems to evaluate on
    BUDGET = 0.05 # budget for evaluation in dollars
    MODEL_ENDPOINT_ID = "gpt-4o-mini" # model endpoint id

    # running the evaluation
    main(
        train_csv_path=TRAIN_CSV_PATH,
        test_csv_path=TEST_CSV_PATH,
        agent_json_file=AGENT_JSON_FILE,
        n_problems=N_PROBLEMS,
        budget=BUDGET,
        model_endpoint_id=MODEL_ENDPOINT_ID,
    )

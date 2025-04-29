"""Copyright (c) 2024, Inria.

Pre-release Version - DO NOT DISTRIBUTE
This software is licensed under the MIT License. See LICENSE for details.
"""

import asyncio
import sys
from datetime import UTC, datetime
from pathlib import Path
from dotenv import load_dotenv
from loguru import logger

from ebiose.core.evo_forging_cycle import EvoForgingCycleConfig
from examples.math_forge.math_forge import MathLangGraphForge

logger.remove()
logger.add(sys.stderr, level="DEBUG")

def main(
        train_csv_path: str,
        test_csv_path: str,
        n_problems: int,
        budget: float,
        save_path: Path,
        default_model_endpoint_id: str | None = None,
    ) -> None:

    forge = MathLangGraphForge(
        train_csv_path=train_csv_path,
        test_csv_path=test_csv_path,
        n_problems=n_problems,
        default_model_endpoint_id=default_model_endpoint_id,  
    )

    cycle_config = EvoForgingCycleConfig(
        budget=budget,
        n_agents_in_population=2,
        n_selected_agents_from_ecosystem=0,
        n_best_agents_to_return=2,
        replacement_ratio=0.5,
        save_path=save_path,
    )

    logger.debug("Running new cycle...")
    result = asyncio.run(forge.run_new_cycle(config=cycle_config))

    if result:
        best_agents, best_finess = result
        if isinstance(best_agents, list):
            logger.warning("best_agents is a list, converting to dictionary format.")
            best_agents = {f"agent_{i}": agent for i, agent in enumerate(best_agents)}

        if isinstance(best_finess, list):
            logger.warning("best_finess is a list, converting to dictionary format.")
            best_finess = {f"agent_{i}": fitness for i, fitness in enumerate(best_finess)}
        
        logger.info(f"Best agents and their fitness: {best_agents}, {best_finess}")
    else:
        logger.error("No results returned from the cycle. Check the agent initialization and fitness evaluation.")
        best_agents, best_finess = {}, {}

    forge.display_results(best_agents, best_finess)

if __name__ == "__main__":
    load_dotenv()

    timestamp = datetime.now(tz=UTC).strftime("%Y-%m-%d_%H-%M-%S")
    SAVE_PATH = Path(f"./data/{timestamp}/")
    if not SAVE_PATH.exists():
        SAVE_PATH.mkdir(parents=True)

    logger.remove()
    logger.add(sys.stderr, level="DEBUG")
    logger.add(SAVE_PATH / "all_logs.log", rotation="10 MB", level="DEBUG")

    BUDGET = 0.05  
    N_PROBLEMS = 2
    TRAIN_CSV_PATH = "./examples/math_forge/gsm8k_train.csv"
    TEST_CSV_PATH = "./examples/math_forge/gsm8k_test.csv"
    DEFAULT_MODEL_ENDPOINT_ID = "azure-gpt-4o-mini" 

    main(
        train_csv_path=TRAIN_CSV_PATH,
        test_csv_path=TEST_CSV_PATH,
        n_problems=N_PROBLEMS,
        budget=BUDGET,
        save_path=SAVE_PATH,
        default_model_endpoint_id=DEFAULT_MODEL_ENDPOINT_ID,
    )

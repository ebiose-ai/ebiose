import asyncio
import sys
from datetime import UTC, datetime
from pathlib import Path

from dotenv import load_dotenv
from loguru import logger

from ebiose.core.evo_forging_cycle import EvoForgingCylceConfig
from examples.math_forge.math_forge import MathLangGraphForge

load_dotenv()

# the path where results will be saved
timestamp = datetime.now(tz=UTC).strftime("%Y-%m-%d_%H-%M-%S")
SAVE_PATH = Path(f"./data/{timestamp}/")
if not SAVE_PATH.exists():
    SAVE_PATH.mkdir(parents=True)

logger.remove()
logger.add(sys.stderr, level="DEBUG")
logger.add(SAVE_PATH / "all_logs.log", rotation="10 MB", level="DEBUG")


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
    n_best_agents_to_return=2,
    replacement_ratio=0.5,
    save_path=SAVE_PATH,
)

best_agents, best_finess = asyncio.run(forge.run_new_cycle(config=cycle_config))

logger.info("Best agents and their fitness:")
forge.display_results(best_agents, best_finess)


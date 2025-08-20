"""Copyright (c) 2024, Inria.

Pre-release Version - DO NOT DISTRIBUTE
This software is licensed under the MIT License. See LICENSE for details.
"""

from __future__ import annotations

import asyncio
import json
import random
import sys
from dataclasses import dataclass, field
from pathlib import Path
from time import time
from typing import TYPE_CHECKING, Literal
from uuid import uuid4

from IPython import get_ipython
from pydantic import BaseModel

from ebiose.core.llm_api_factory import LLMApiFactory
from ebiose.cloud_client.ebiose_api_client import EbioseAPIClient

from ebiose.core.events import (
    AgentAddedToPopulationEvent,
    AgentEvaluationCompletedEvent,
    ArchitectAgentTaskCreatedEvent,
    AgentSelectionCompletedEvent,
    AgentSelectionStartedEvent,
    CrossoverAndMutationCompletedEvent,
    CrossoverAndMutationStartedEvent,
    ForgeCycleEndedEvent,
    ForgeCycleFailedEvent,
    ForgeCycleStartedEvent,
    GenerationRunCompletedEvent,
    GenerationRunStartedEvent,
    OffspringCreatedEvent,
    PopulationEvaluationCompletedEvent,
    PopulationEvaluationStartedEvent,
    PopulationInitializationCompletedEvent,
    PopulationInitializationStartedEvent,
    init_logger,
)
from ebiose.core.model_endpoint import ModelEndpoints

if get_ipython() is not None:
    pass

from loguru import logger
from tqdm.asyncio import tqdm

from ebiose.core.agent import Agent
from ebiose.tools.agent_generation_task_with_fallback import (
    architect_agent_task,
    crossover_agent_task,
)

if TYPE_CHECKING:
    from ebiose.core.agent_forge import AgentForge
    from ebiose.core.ecosystem import Ecosystem
    from ebiose.core.llm_api import LLMApi


import datetime

MIN_PARENTS_FOR_CROSSOVER = 2
MIN_TOURNAMENT_SIZE = 2

if get_ipython() is not None:
    logger.remove()
    logger.add(sys.stderr, format="<level>{message}</level>", level="DEBUG")

def human_readable_duration(start_time: float) -> str:
    elapsed_time = time() - start_time
    return str(datetime.timedelta(seconds=elapsed_time))


class ForgeCycleConfig(BaseModel):
    n_agents_in_population: int = 10
    n_selected_agents_from_ecosystem: int = 5
    n_best_agents_to_return: int = 3
    replacement_ratio: float = 0.5
    tournament_size_ratio: float = 0.1
    local_results_path: Path | None = None
    mode: Literal["local", "cloud"]


class CloudForgeCycleConfig(ForgeCycleConfig):
    budget: float
    mode: Literal["local", "cloud"] = "cloud"

class LocalForgeCycleConfig(ForgeCycleConfig):
    n_generations: int
    mode: Literal["local", "cloud"] = "local"


@dataclass
class ForgeCycle:
    forge: AgentForge
    config: ForgeCycleConfig
    id: str = field(default_factory=lambda: f"forge-cycle-{uuid4()!s}")  # Changed Pydantic Field to dataclasses.field

    cur_generation: int = 0
    llm_api: LLMApi | None = None

    agents: dict[str, Agent] = field(default_factory=dict)
    agents_fitness: dict[str, float] = field(default_factory=dict)
    agents_first_generation_costs: dict[str, float] = field(default_factory=dict)
    init_agents_population: dict[Agent] = field(default_factory=list)

    architect_agents: dict[str, Agent] = field(default_factory=dict)
    genetic_operator_agents: dict[str, Agent] = field(default_factory=dict)

    def save_current_state(self, generation: int | None = None) -> None:
        if self.config.local_results_path is not None:
            if generation is not None:
                full_save_path = Path(self.config.local_results_path) / f"generation={generation}"
            else:
                full_save_path = Path(self.config.local_results_path) / "init"
            if not Path.exists(full_save_path):
                Path.mkdir(full_save_path, parents=True)
            logger.debug(f"Saving current state to {full_save_path}")

            # save agents
            agents_folder = Path(full_save_path) / "agents"
            self._save_agents(agents_folder)

            # save fitness
            fitness_file = Path(full_save_path) / "fitness.json"
            with Path.open(fitness_file, "w") as fitness_file:
                fitness_file.write(json.dumps(self.agents_fitness, indent=4))

    def _save_agents(self, agents_folder: str) -> None:
        if not Path.exists(agents_folder):
            Path.mkdir(agents_folder, parents=True)

        for agent_id, agent in self.agents.items():
            agent_file_path = Path(agents_folder) / f"{agent_id}.json"
            json_str = agent.model_dump_json(indent=4)
            with Path.open(agent_file_path, "w") as agent_file:
                agent_file.write(json_str)

    def get_budget_info(self) -> tuple[float | None, float | None]:
        """Get current budget information for events.

        Returns:
            tuple: (remaining_budget, initial_budget) or (None, None) if not in cloud mode
        """
        if self.config.mode == "cloud" and hasattr(self.config, "budget"):
            total_cost = self.llm_api.get_total_cost(forge_cycle_id=self.id)
            remaining_budget = self.config.budget - total_cost
            return remaining_budget, self.config.budget
        return None, None

    def add_agent(self, agent: Agent, source: str) -> None:
        try:
            if self.config.mode == "cloud" and source != "kept_from_previous_gen":
                # TODO(xabier): improve condition to avoid pushing an agent twice
                agent_id = EbioseAPIClient.add_agent_from_forge_cycle(
                    forge_cycle_id=self.id,
                    agent=agent,
                )
                agent.id = agent_id
                agent.agent_engine.agent_id = agent_id  # Ensure agent's engine has the correct ID
            self.agents[agent.id] = agent
            remaining_budget, initial_budget = self.get_budget_info()
            AgentAddedToPopulationEvent(
                agent_id=agent.id,
                generation_number=self.cur_generation,
                source=source,
                agent=agent.model_dump(
                    mode="json",
                    exclude={"agent_engine", "description_embedding"},
                ),
                remaining_budget=remaining_budget,
                initial_budget=initial_budget,
            ).log()
        except Exception as e:
            logger.debug(f"Error while adding an agent: {e!s}, {agent}")

    def check_agent_type(self, agent: Agent) -> None:
        # TODO(xabier): replace this method by a "agent_type" field in Agent class
        if "parent_configuration1" in agent.agent_engine.input_model.model_fields:
            return "crossover"
        if "parent_configuration" in agent.agent_engine.input_model.model_fields:
            return "mutation"
        if "random_n_llm_nodes" in agent.agent_engine.input_model.model_fields:
            return "architect"
        return "standard"

    def get_agents_by_type(self, agent_type: Literal["architect", "crossover", "mutation", "standard"]) -> dict[str, Agent]:
        if agent_type == "architect":
            return self.architect_agents
        if agent_type == "standard":
            return self.agents
        return {
            agent_id: agent for agent_id, agent in self.genetic_operator_agents.items() \
                if agent_type == self.check_agent_type(agent)
        }

    async def initialize_population(self, ecosystem: Ecosystem) -> None: # Removed quotes from Ecosystem type hint
        logger.info("****** Initializing agents population ******")
        remaining_budget, initial_budget = self.get_budget_info()
        PopulationInitializationStartedEvent(
            n_agents_to_initialize=self.config.n_agents_in_population,
            n_selected_from_ecosystem=self.config.n_selected_agents_from_ecosystem,
            remaining_budget=remaining_budget,
            initial_budget=initial_budget,
        ).log()
        init_pop_start_time = time()

        self.agents.clear()
        self.agents_first_generation_costs.clear()

        n_selected_agents = self.config.n_selected_agents_from_ecosystem
        selected_agents = []
        if self.config.mode == "cloud":
            selected_agents = EbioseAPIClient.select_agents(
                nb_agents=n_selected_agents,
                forge_cycle_uuid=self.id,
            )
            for selected_agent in selected_agents:
                selected_agent.update_io_models(
                    agent_input_model=self.forge.agent_input_model,
                    agent_output_model=self.forge.agent_output_model,
                )
            self.load_meta_agents_from_ecosystem(ecosystem)

        logger.debug(f"{len(selected_agents)} agents selected from ecosystem over {n_selected_agents} requested")


        # Initialize population
        tasks = []
        if n_selected_agents == 0 or len(selected_agents) == 0:
            # when no agents are selected from the ecosystem
            logger.info(f"Creating {self.config.n_agents_in_population} new agents with architect agents...")
            for _ in range(self.config.n_agents_in_population):
                architect_agent = random.choice(ecosystem.initial_architect_agents)
                architect_agent_input = architect_agent.agent_engine.input_model(
                    forge_description=self.forge.description,
                )
                genetic_operator_agent = random.choice(ecosystem.initial_genetic_operator_agents)

                task = architect_agent_task(
                    forge=self.forge,
                    architect_agent=architect_agent,
                    architect_agent_input=architect_agent_input,
                    genetic_operator_agent=genetic_operator_agent,
                    forge_cycle_id=self.id,
                )
                remaining_budget, initial_budget = self.get_budget_info()
                ArchitectAgentTaskCreatedEvent(
                    architect_agent_id=architect_agent.id,
                    generation_number=self.cur_generation,
                    remaining_budget=remaining_budget,
                    initial_budget=initial_budget,
                ).log()
                tasks.append(task)
        else:
            # when some agents are selected from the ecosystem
            logger.info(f"{len(selected_agents)} selected agents from ecosystem. Creating {self.config.n_agents_in_population - len(selected_agents)} agents...")

            while len(tasks) < (self.config.n_agents_in_population - len(selected_agents)):
                for selected_agent in selected_agents:
                    if len(tasks) >= self.config.n_agents_in_population:
                        break

                    # TODO(xabier): if selected agent is an architect agent
                    # it does not have an architect agent...
                    architect_agent = self.architect_agents[selected_agent.architect_agent_id]
                    architect_agent_input = architect_agent.agent_engine.input_model(
                        forge_description=self.forge.description,
                    )
                    genetic_operator_agent = None
                    if selected_agent.genetic_operator_agent_id is not None:
                        genetic_operator_agent = self.genetic_operator_agents[selected_agent.genetic_operator_agent_id]

                    task = architect_agent_task(
                        forge=self.forge,
                        architect_agent=architect_agent,
                        architect_agent_input=architect_agent_input,
                        genetic_operator_agent=genetic_operator_agent,
                        forge_cycle_id=self.id,
                    )
                    remaining_budget, initial_budget = self.get_budget_info()
                    ArchitectAgentTaskCreatedEvent(
                        architect_agent_id=architect_agent.id,
                        generation_number=self.cur_generation,
                        remaining_budget=remaining_budget,
                        initial_budget=initial_budget,
                    ).log()
                    tasks.append(task)

        results = await tqdm.gather(*tasks)

        for selected_agent in selected_agents if n_selected_agents > 0 else []:
            self.add_agent(selected_agent, source="from_ecosystem")

        for new_agent in results:
            if new_agent is None:
                continue
            self.add_agent(new_agent, source="newly_created_during_init")

        initialization_cost = self.llm_api.get_total_cost()
        remaining_budget, initial_budget = self.get_budget_info()
        PopulationInitializationCompletedEvent(
            num_agents_initialized=len(self.agents),
            initialization_cost=initialization_cost,
            duration_seconds=time() - init_pop_start_time,
            remaining_budget=remaining_budget,
            initial_budget=initial_budget,
        ).log()

        return initialization_cost

    def load_meta_agents_from_ecosystem(
        self, ecosystem: Ecosystem,
    ) -> None:
        #TODO(xabier): this should be used to get architect and genetic operator agents
        # only after agents are selected from the ecosystem
        # self.agents = {
        # _id: agent for _id, agent in ecosystem.agents.items()
        # if agent.agent_type is None
        # }

        meta_agent_endpoint_id = ModelEndpoints.get_default_meta_agent_endpoint_id()
        self.architect_agents = {
            _id: agent for _id, agent in ecosystem.agents.items()
            if agent.agent_type == "architect"
        }
        self.genetic_operator_agents = {
            _id: agent for _id, agent in ecosystem.agents.items()
            if agent.agent_type == "genetic_operator"
        }

        for agent in self.architect_agents.values():
            agent.agent_engine.tags = ["architect_agent"]

        for agent in self.genetic_operator_agents.values():
            agent.agent_engine.tags = ["genetic_operator_agent"]

        if meta_agent_endpoint_id is not None:
            # Set the model endpoint ID for each meta agent
            for agent in self.architect_agents.values():
                agent.agent_engine.model_endpoint_id = meta_agent_endpoint_id
            for agent in self.genetic_operator_agents.values():
                agent.agent_engine.model_endpoint_id = meta_agent_endpoint_id



    async def execute_a_cycle(
            self,
            ecosystem: Ecosystem | None, # Removed quotes from Ecosystem type hint
            lite_llm_api_key: str | None = None,
        ) -> tuple[dict[str, Agent], dict[str, float]]:

        cycle_start_time = time()
        total_cycle_cost = 0.0

        lite_llm_api_key = None
        user_id = None
        if self.config.mode == "cloud":
            ecosystem_uuid = EbioseAPIClient.get_first_ecosystem_uuid()
            ecosystem = EbioseAPIClient.get_ecosystem(ecosystem_uuid)
            # call cloud start forge cycle
            # returns: lite llm api key and forge cycle id
            lite_llm_api_key, lite_llm_api_base, forge_cycle_id, forge_id = EbioseAPIClient.start_new_forge_cycle(
                ecosystem_id=ecosystem_uuid,
                forge_name=self.forge.name,
                forge_description=self.forge.description,
                forge_cycle_config=self.config,
                override_key=True, #TODO(xabier): see how to do this properly
            )
            self.id = forge_cycle_id
            user_id = EbioseAPIClient.get_user_id()

        init_logger(
            user_id=user_id,
            forge_id=forge_id,
            forge_cycle_id=self.id,
            initial_budget=self.config.budget
            if self.config.mode == "cloud" and hasattr(self.config, "budget")
            else None,
        )

        self.llm_api = LLMApiFactory.initialize(
            mode=self.config.mode,
            lite_llm_api_key=lite_llm_api_key,
            lite_llm_api_base=lite_llm_api_base,
        )

        remaining_budget, initial_budget = self.get_budget_info()
        ForgeCycleStartedEvent(
            forge_name=self.forge.name,
            forge_description=self.forge.description,
            config=self.config.model_dump(mode="json"),
            remaining_budget=remaining_budget,
            initial_budget=initial_budget,
        ).log()

        if ecosystem is None :
            # TODO(xabier): this does not work
            from ebiose.core.ecosystem import Ecosystem
            ecosystem = Ecosystem.new()

        

        try:
            t0 = time()
            total_cycle_cost = 0
            initialization_cost = await self.initialize_population(ecosystem=ecosystem)
            # cancel run if no agent was initialized
            if len(self.agents) == 0:
                logger.info("No agent was initialized. Exiting cycle. Check the logs for more information.")
                remaining_budget, initial_budget = self.get_budget_info()
                ForgeCycleFailedEvent(
                    error_message="No agent was initialized",
                    duration_seconds=time() - cycle_start_time,
                    remaining_budget=remaining_budget,
                    initial_budget=initial_budget,
                ).log()
                selected_agents, selected_fitness = {}, {}
                return selected_agents, selected_fitness

            total_cycle_cost += initialization_cost
            logger.info(f"Budget left after initialization: {self.config.budget - total_cycle_cost} $")

            # running generation 1
            self.cur_generation += 1
            first_evaluation_cost, first_genetic_cost = await self.run_generation()
            estimated_cost_to_complete_cycle = 2 * first_evaluation_cost + first_genetic_cost
            total_cycle_cost += first_evaluation_cost + first_genetic_cost

            # running next generations until budget is reached
            while self.config.budget - total_cycle_cost > estimated_cost_to_complete_cycle \
                if self.config.mode == "cloud" \
                else self.cur_generation < self.config.n_generations:
                self.cur_generation += 1
                evaluation_cost, genetic_cost = await self.run_generation()
                total_cycle_cost += evaluation_cost + genetic_cost

            # Evaluate last offsprings before sorting all population by fitness
            total_cycle_cost += await self._evaluate_population()
            # TODO(xabier): this is a hack to save last evaluation
            self.save_current_state(self.cur_generation+1)

            # Distribute total cycle cost among agents based on their initialization costs
            total_init_cost = sum(self.agents_first_generation_costs.values())
            for agent_id, init_cost in self.agents_first_generation_costs.items():
                cost_ratio = init_cost / total_init_cost if total_init_cost > 0 else 0
                agent_cycle_cost = cost_ratio * total_cycle_cost
                self.agents_first_generation_costs[agent_id] = agent_cycle_cost

            sorted_agents = sorted(
                self.agents.values(),
                key=lambda agent: self.agents_fitness[agent.id],
                reverse=True,
            )

        except Exception as e:
            logger.error(f"Error during cycle execution: {e!s}")
            logger.info("Cycle execution failed. Cleaning up...")
            remaining_budget, initial_budget = self.get_budget_info()
            ForgeCycleFailedEvent(
                error_message=str(e),
                duration_seconds=time() - cycle_start_time,
                remaining_budget=remaining_budget,
                initial_budget=initial_budget,
            ).log()
            selected_agents, selected_fitness = {}, {}
        else:
            logger.info(f"Cycle completed in {human_readable_duration(t0)} with a total cost of {total_cycle_cost} $")
            if self.config.mode == "cloud":
                logger.info(f"Budget left at final: {self.config.budget - self.llm_api.get_total_cost()} $")
            logger.info(f"Returning {self.config.n_best_agents_to_return} best agents")

            selected_agents = {
                agent.id: agent for agent in sorted_agents[:self.config.n_best_agents_to_return]
            }
            selected_fitness = {agent_id: self.agents_fitness[agent_id] for agent_id in selected_agents}
            remaining_budget, initial_budget = self.get_budget_info()
            ForgeCycleEndedEvent(
                duration_seconds=time() - cycle_start_time,
                total_cost=total_cycle_cost,
                num_best_agents=len(selected_agents),
                remaining_budget=remaining_budget,
                initial_budget=initial_budget,
            ).log()
            return selected_agents, selected_fitness

        finally:
            # Clean up
            if self.config.mode == "cloud":
                EbioseAPIClient.end_forge_cycle(
                    forge_cycle_uuid=forge_cycle_id,
                    winning_agents=list(selected_agents.values()),
                )

    async def run_generation(self) -> tuple[float, float]:
        logger.info(f"****** Running generation {self.cur_generation} ******")
        gen_start_time = time()
        remaining_budget, initial_budget = self.get_budget_info()
        GenerationRunStartedEvent(
            generation_number=self.cur_generation,
            current_population_size=len(self.agents),
            remaining_budget=remaining_budget,
            initial_budget=initial_budget,
        ).log()
        # Evaluate current population asynchronously
        logger.info(f"Evaluating current population of {len(self.agents)} agents...")
        t0 = time()
        evaluation_cost = await self._evaluate_population()
        logger.info(f"Evaluation took {human_readable_duration(t0)} for a total cost of {evaluation_cost} $")
        self.display_current_results()
        self.save_current_state(self.cur_generation)

        # Select agents for crossover and mutation
        # number of agents to be replaced
        n_replaced = int(self.config.n_agents_in_population * self.config.replacement_ratio)
        # number of agents to be kept
        n_kept = self.config.n_agents_in_population - n_replaced
        # we randomly select the agents that will be kept
        kept_agents = self.roulette_wheel_selection(n_kept)

        # Tournament selection for crossover
        logger.info("Starting crossover and mutation...")
        selected_parent_ids_for_crossover = self.tournament_selection(n_to_select=n_replaced)
        if selected_parent_ids_for_crossover is None or len(selected_parent_ids_for_crossover) == 0:
            # TODO (xabier): throw and error or fallback to architect agents?
            logger.warning("No parents selected for crossover. This may lead to no new agents being created.")
        t1 = time()
        offspring_agents, genetic_cost = await self.crossover_and_mutate(selected_parent_ids_for_crossover)
        logger.info(f"Crossover and mutation completed in {human_readable_duration(t1)} for a total cost of {genetic_cost} $")

        # we finally add kept and offspring agents
        # Clear and repopulate agents and fitness, log 'kept_from_previous_gen' source
        self.agents.clear()
        self.agents_fitness.clear()

        for agent_id, agent_obj in kept_agents.items():
            self.add_agent(agent_obj, source="kept_from_previous_gen")
            # avoiding to recompute fitness has to be handled by the forge
            # self.agents_fitness[agent_id] = current_agents_fitness[agent_id]


        for offspring in offspring_agents:
            self.add_agent(offspring, source="offspring")

        logger.info(f"Generation {self.cur_generation} completed in {human_readable_duration(t0)} with a total cost of TODO $")
        remaining_budget, initial_budget = self.get_budget_info()
        GenerationRunCompletedEvent(
            generation_number=self.cur_generation,
            generation_total_cost=evaluation_cost + genetic_cost,
            duration_seconds=time() - gen_start_time,
            population_size_after_generation=len(self.agents),
            remaining_budget=remaining_budget,
            initial_budget=initial_budget,
        ).log()
   
        return evaluation_cost, genetic_cost


    async def _evaluate_population(self) -> float:
        remaining_budget, initial_budget = self.get_budget_info()
        PopulationEvaluationStartedEvent(
            generation_number=self.cur_generation,
            num_agents_to_evaluate=len(self.agents),
            remaining_budget=remaining_budget,
            initial_budget=initial_budget,
        ).log()
        eval_start_time = time()
        tasks = []
        for agent in self.agents.values():
            task = asyncio.create_task(
                self.forge.compute_fitness(agent, generation=self.cur_generation, forge_cycle_id=self.id),
            )
            tasks.append(task)

        results = await tqdm.gather(*tasks)

        update_first_generation_costs = (self.cur_generation == 0)
        total_cost_in_dollars = 0
        for agent_id, fitness in results:
        # for index, agent_id in enumerate(self.agents.keys()):
            # fitness = results[index]
            self.agents_fitness[agent_id] = fitness
            current_agent_cost = self.llm_api.get_agent_cost(agent_id)
            total_cost_in_dollars += current_agent_cost
            remaining_budget, initial_budget = self.get_budget_info()
            AgentEvaluationCompletedEvent(
                agent_id=agent_id,
                generation_number=self.cur_generation,
                fitness=fitness,
                evaluation_cost=current_agent_cost,
                remaining_budget=remaining_budget,
                initial_budget=initial_budget,
            ).log()

            if update_first_generation_costs:
                if agent_id not in self.agents_first_generation_costs:
                    self.agents_first_generation_costs[agent_id] = 0
                self.agents_first_generation_costs[agent_id] += current_agent_cost

            logger.debug(f"Agent {agent_id} fitness: {fitness}, cost: {current_agent_cost}")

        remaining_budget, initial_budget = self.get_budget_info()
        PopulationEvaluationCompletedEvent(
            generation_number=self.cur_generation,
            total_evaluation_cost=total_cost_in_dollars,
            duration_seconds=time() - eval_start_time,
            remaining_budget=remaining_budget,
            initial_budget=initial_budget,
        ).log()

        if len(self.agents) != len(self.agents_fitness):
            logger.warning("Mismatch between number of agents and fitness values.")
        if set(self.agents.keys()) != set(self.agents_fitness.keys()):
            logger.warning("Mismatch between agent IDs and fitness values.")

        return total_cost_in_dollars


    def roulette_wheel_selection(self, n_to_select: int) -> dict[str, Agent]:
        remaining_budget, initial_budget = self.get_budget_info()
        AgentSelectionStartedEvent(
            generation_number=self.cur_generation,
            method="roulette_wheel",
            num_to_select=n_to_select,
            remaining_budget=remaining_budget,
            initial_budget=initial_budget,
        ).log()
        selected_agents = {}
        if not self.agents_fitness:
            logger.warning("No fitness values available for roulette wheel selection.")
            remaining_budget, initial_budget = self.get_budget_info()
            AgentSelectionCompletedEvent(
                generation_number=self.cur_generation,
                method="roulette_wheel",  # Added missing field
                num_selected=0,
                selected_agent_ids=[],
                remaining_budget=remaining_budget,
                initial_budget=initial_budget,
            ).log()
            return selected_agents

        # Calculate total fitness
        total_fitness = sum(self.agents_fitness.values())
        for _ in range(n_to_select):
            pick = random.uniform(0, total_fitness)
            current = 0
            for agent_id, fitness in self.agents_fitness.items():
                current += fitness
                if current >= pick:
                    selected_agent = self.agents[agent_id]
                    selected_agents[selected_agent.id] = selected_agent
                    break

        logger.debug(f"Selected {len(selected_agents)} agents using roulette wheel selection: {list(selected_agents.keys())}")
        remaining_budget, initial_budget = self.get_budget_info()
        AgentSelectionCompletedEvent(
            generation_number=self.cur_generation,
            method="roulette_wheel",  # Added missing field
            num_selected=len(selected_agents),
            selected_agent_ids=list(selected_agents.keys()),
            remaining_budget=remaining_budget,
            initial_budget=initial_budget,
        ).log()
        return selected_agents

    def tournament_selection(self, n_to_select: int) -> list[str]:
        # 1. each agent participates in exactly one tournament
        # 2. the best agents of each tournament are selected
        # 3. amongst them, x% are randomly selected to replace the parents of the next generation
        # 4. the others are kept
        remaining_budget, initial_budget = self.get_budget_info()
        AgentSelectionStartedEvent(
            generation_number=self.cur_generation,
            method="tournament",
            num_to_select=n_to_select,
            remaining_budget=remaining_budget,
            initial_budget=initial_budget,
        ).log()
        selected_ids = []
        if not self.agents:
            logger.warning("No agents available for tournament selection.")
            remaining_budget, initial_budget = self.get_budget_info()
            AgentSelectionCompletedEvent(
                generation_number=self.cur_generation,
                method="tournament",  # Added missing field
                num_selected=0,
                selected_agent_ids=[],
                remaining_budget=remaining_budget,
                initial_budget=initial_budget,
            ).log()
            return selected_ids

        tournament_size = max(MIN_TOURNAMENT_SIZE, int(self.config.tournament_size_ratio * len(self.agents)))
        winning_agent_ids = []
        agents = list(self.agents.values())
        for i, agent in enumerate(agents):
            tournament_agents = [agent]
            # pick tournament_size agents at random, except the agent itself
            # TODO(xabier): to be fixed because we should not select the same agent twice
            if len(agents) <= 1:
                tournament_agents += [agents[0]] * (tournament_size - 1)
            else:
                tournament_agents += random.sample(agents[:i] + agents[i+1:], tournament_size-1)
            tournament_fitness = [self.agents_fitness[agent.id] for agent in tournament_agents]
            best_agent = tournament_agents[tournament_fitness.index(max(tournament_fitness))]
            winning_agent_ids.append(best_agent.id)

        # WARNING: we should not select the same agent twice
        selected_ids = random.choices(winning_agent_ids, k=n_to_select)

        logger.debug(f"Selected {len(selected_ids)} agents using tournament selection: {selected_ids}")
        remaining_budget, initial_budget = self.get_budget_info()
        AgentSelectionCompletedEvent(
            generation_number=self.cur_generation,
            method="tournament",  # Added missing field
            num_selected=len(selected_ids),
            selected_agent_ids=selected_ids,
            remaining_budget=remaining_budget,
            initial_budget=initial_budget,
        ).log()
        return selected_ids

    async def crossover_and_mutate(self, selected_parent_ids: list[str]) -> tuple[list[Agent], float]:
        remaining_budget, initial_budget = self.get_budget_info()
        CrossoverAndMutationStartedEvent(
            generation_number=self.cur_generation,
            num_parents=len(selected_parent_ids),
            remaining_budget=remaining_budget,
            initial_budget=initial_budget,
        ).log()

        crossover_start_time = time()
        previous_cost = self.llm_api.get_total_cost()
        offsprings = []
        tasks = []

        if len(selected_parent_ids) == 0:
            # No parents for crossover or mutation
            # TODO(xabier) should fallback to architect agents?
            return [], 0.0

        # Single parent: fallback to mutation  
        if len(selected_parent_ids) == 1:
            parent_id = selected_parent_ids[0]
            parent = self.agents[parent_id]
            architect_agent = self.architect_agents.get(parent.architect_agent_id)


            # Select mutation agent: embedded or random
            mut_agent_id = parent.genetic_operator_agent_id
            mut_agent = self.genetic_operator_agents[mut_agent_id]
            if self.check_agent_type(mut_agent) != "mutation":
                # If the agent is not a mutation agent, we fallback to a random mutation agent
                mut_agents = self.get_agents_by_type("mutation")
                mut_agent = random.choice(list(mut_agents.values())) if mut_agents else None
            if mut_agent is None:
                # TODO(xabier): fallback to architect agent?
                logger.warning(f"No mutation agent found for parent {parent_id}. Cannot perform mutation.")
                return [], 0.0

            # Build mutation input
            mutation_input = mut_agent.agent_engine.input_model(
                forge_description=self.forge.description,
                parent_configuration=parent.agent_engine.graph.model_dump(),
            )
            # Schedule mutation task
            task = crossover_agent_task(
                forge=self.forge,
                genetic_operator_agent=mut_agent,
                crossover_agent_input=mutation_input,
                architect_agent=architect_agent,
                parent1=parent,
                parent2=None,
                master_agent_id=None,
                forge_cycle_id=self.id,
            )
            tasks.append(task)
        else:
            # Standard crossover for parent pairs
            for p1_id in selected_parent_ids:
                other_ids = [sp_id for sp_id in selected_parent_ids if sp_id != p1_id]
                p2_id = random.choice(other_ids) if other_ids else p1_id
                parent1 = self.agents[p1_id]
                parent2 = self.agents[p2_id]
                if p1_id == p2_id:
                    # Same parent twice: fallback to mutation
                    agent = parent1
                    mut_id = agent.genetic_operator_agent_id or random.choice(list(self.genetic_operator_agents.keys()))
                    mut_agent = self.genetic_operator_agents[mut_id]
                    architect_agent = self.architect_agents.get(agent.architect_agent_id)
                    if self.check_agent_type(mut_agent) != "mutation":
                        # If the agent is not a mutation agent, we fallback to a random mutation agent
                        mut_agents = self.get_agents_by_type("mutation")
                        mut_agent = random.choice(list(mut_agents.values())) if mut_agents else None
                    if mut_agent is None:
                        # TODO(xabier): fallback to architect agent?
                        logger.warning(f"No mutation agent found for parent {parent_id}. Cannot perform mutation.")
                        return [], 0.0
                    mutation_input = mut_agent.agent_engine.input_model(
                        forge_description=self.forge.description,
                        parent_configuration=agent.agent_engine.graph.model_dump(),
                    )
                    task = crossover_agent_task(
                        forge=self.forge,
                        genetic_operator_agent=mut_agent,
                        crossover_agent_input=mutation_input,
                        architect_agent=architect_agent,
                        parent1=agent,
                        parent2=None,
                        master_agent_id=None,
                        forge_cycle_id=self.id,
                    )
                else:
                    # True crossover
                    # Select one of the parents' mutation/crossover agents
                    chosen_id = random.choice([p1_id, p2_id])
                    gen_op_id = self.agents[chosen_id].genetic_operator_agent_id
                    gen_op_agent = self.genetic_operator_agents[gen_op_id]
                    architect_agent = self.architect_agents.get(self.agents[chosen_id].architect_agent_id)
                    if gen_op_agent.name == "crossover_agent":
                        input_model = gen_op_agent.agent_engine.input_model(
                            forge_description=self.forge.description,
                            parent_configuration1=parent1.agent_engine.graph.model_dump(),
                            parent_configuration2=parent2.agent_engine.graph.model_dump(),
                        )
                    else:
                        input_model = gen_op_agent.agent_engine.input_model(
                            forge_description=self.forge.description,
                            parent_configuration=parent1.agent_engine.graph.model_dump(),
                        )
                        parent2 = None
                    task = crossover_agent_task(
                        forge=self.forge,
                        genetic_operator_agent=gen_op_agent,
                        crossover_agent_input=input_model,
                        parent1=parent1,
                        parent2=parent2,
                        master_agent_id=None,
                        forge_cycle_id=self.id,
                        architect_agent=architect_agent,
                    )
                tasks.append(task)
        results = await tqdm.gather(*tasks)
        for offspring_agent in results:
            if offspring_agent is not None:
                offsprings.append(offspring_agent)
                remaining_budget, initial_budget = self.get_budget_info()
                OffspringCreatedEvent(
                    offspring_agent_id=offspring_agent.id,
                    generation_number=self.cur_generation,
                    parent_ids=offspring_agent.parent_ids,
                    genetic_operator_agent_id=offspring_agent.genetic_operator_agent_id,
                    offspring_agent=offspring_agent.model_dump(
                        mode="json",
                        exclude={"agent_engine", "description_embedding"},
                    ),
                    remaining_budget=remaining_budget,
                    initial_budget=initial_budget,
                ).log()

        current_phase_cost = self.llm_api.get_total_cost() - previous_cost
        remaining_budget, initial_budget = self.get_budget_info()
        CrossoverAndMutationCompletedEvent(
            generation_number=self.cur_generation,
            num_offsprings_generated=len(offsprings),
            duration_seconds=time() - crossover_start_time,
            cost=current_phase_cost,  # This needs accurate calculation
            remaining_budget=remaining_budget,
            initial_budget=initial_budget,
        ).log()
        return offsprings, current_phase_cost


    def display_current_results(self, n_best: int = 3) -> None:
        sorted_fitness = dict(sorted(self.agents_fitness.items(), key=lambda item: item[1], reverse=True))
        best_ids = list(sorted_fitness.keys())[:n_best]
        best_agents = {agent_id: self.agents[agent_id] for agent_id in best_ids}
        best_agents_fitness = {agent_id: sorted_fitness[agent_id] for agent_id in best_ids}
        self.forge.display_results(best_agents, best_agents_fitness)

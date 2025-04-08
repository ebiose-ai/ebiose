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
from typing import TYPE_CHECKING

from IPython import get_ipython
from pydantic import BaseModel

if get_ipython() is not None:
    pass

from loguru import logger
from tqdm.asyncio import tqdm

from ebiose.compute_intensive_batch_processor.compute_intensive_batch_processor import (
    ComputeIntensiveBatchProcessor,
)
from ebiose.core.agent import Agent
from ebiose.tools.agent_generation_task_with_fallback import (
    architect_agent_task,
    crossover_agent_task,
)

if TYPE_CHECKING:
    from ebiose.core.agent_forge import AgentForge
    from ebiose.core.ecosystem import Ecosystem
import datetime

if get_ipython() is not None:
    logger.remove()
    logger.add(sys.stderr, format="<level>{message}</level>", level="DEBUG")

def human_readable_duration(start_time: float) -> str:
    elapsed_time = time() - start_time
    return str(datetime.timedelta(seconds=elapsed_time))

class EvoForgingCycleConfig(BaseModel):
    budget: float
    n_agents_in_population: int
    n_selected_agents_from_ecosystem: int
    n_best_agents_to_return: int = 3
    architect_agent_budget_ratio: float = 1.0
    genetic_operator_agent_budget_ratio: float = 1.0
    replacement_ratio: float = 0.5
    tournament_size_ratio: float = 0.1
    save_path: Path | None = None
    node_types: list[str] = ["StartNode", "EndNode", "LLMNode"]


@dataclass
class EvoForgingCycle:
    forge: AgentForge
    config: EvoForgingCycleConfig

    _master_compute_token: str | None = None
    _architect_agent_compute_token: str | None = None

    agents: dict[str, Agent] = field(default_factory=dict)
    agents_fitness: dict[str, float] = field(default_factory=dict)
    agents_first_generation_costs: dict[str, float] = field(default_factory=dict)
    init_agents_population: dict[Agent] = field(default_factory=list)

    def save_current_state(self, generation: int | None = None) -> None:
        if self.config.save_path is not None:
            if generation is not None:
                full_save_path = Path(self.config.save_path) / f"generation={generation}"
            else:
                full_save_path = Path(self.config.save_path) / "init"
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

    def add_agent(self, agent: Agent) -> None:
        try:
            self.agents[agent.id] = agent
        except Exception as e:
            logger.debug(f"Error while adding an agent: {e!s}, {agent}")


    async def initialize_population(self, ecosystem: Ecosystem) -> None:
        logger.info("****** Initializing agents population ******")
        self.agents.clear()
        self.agents_first_generation_costs.clear()

        n_selected_agents = self.config.n_selected_agents_from_ecosystem
        if n_selected_agents > 0 :
            selected_agents = await ecosystem.select_agents_for_forge(self.forge, n_selected_agents)
            logger.debug(f"{len(selected_agents)} agents selected from ecosystem over {n_selected_agents} requested")

        # Initialize population
        tasks = []
        if n_selected_agents == 0 or len(selected_agents) == 0:
            logger.info(f"Creating {self.config.n_agents_in_population} new agents with architect agents...")
            for _ in range(self.config.n_agents_in_population):
                architect_agent = random.choice(ecosystem.initial_architect_agents)
                architect_agent_input = architect_agent.agent_engine.input_model(
                    forge_description=self.forge.description,
                    node_types=self.config.node_types,
                )
                genetic_operator_agent = random.choice(ecosystem.initial_genetic_operator_agents)

                task = architect_agent_task(
                    forge=self.forge,
                    architect_agent=architect_agent,
                    architect_agent_input=architect_agent_input,
                    architect_agent_compute_token=self._architect_agent_compute_token,
                    genetic_operator_agent=genetic_operator_agent,
                )
                tasks.append(task)
        else:
            logger.info(f"{len(selected_agents)} selected agents from ecosystem. Creating {self.config.n_agents_in_population - len(selected_agents)}...")

            while len(tasks) < (self.config.n_agents_in_population - len(selected_agents)):
                for selected_agent in selected_agents:
                    if len(tasks) >= self.config.n_agents_in_population:
                        break
                    architect_agent = selected_agent.architect_agent
                    architect_agent_input = architect_agent.agent_engine.input_model(
                        forge_description=self.forge.description,
                        node_types=self.config.node_types,
                    )
                    genetic_operator_agent = selected_agent.genetic_operator_agent

                    task = architect_agent_task(
                        forge=self.forge,
                        architect_agent=architect_agent,
                        architect_agent_input=architect_agent_input,
                        architect_agent_compute_token=self._architect_agent_compute_token,
                        genetic_operator_agent=genetic_operator_agent,
                    )
                    tasks.append(task)

        results = await tqdm.gather(*tasks)

        for selected_agent in selected_agents if n_selected_agents > 0 else []:
            self.add_agent(selected_agent)

        logger.debug(f"Agent initialization cost: {ComputeIntensiveBatchProcessor.get_master_token_cost()}")
        for new_agent in results:
            if new_agent is None:
                continue
            self.add_agent(new_agent)

        logger.info(f"Population initialized with {len(self.agents)} agents")


    async def execute_a_cycle(self, ecosystem: Ecosystem) -> list[Agent]:

        logger.info(f"Starting a new cycle for forge {self.forge.name}")
        ComputeIntensiveBatchProcessor.initialize()
        self._master_compute_token = ComputeIntensiveBatchProcessor.acquire_master_token(budget=self.config.budget)
        self._architect_agent_compute_token = ComputeIntensiveBatchProcessor.generate_token(
            self.config.architect_agent_budget_ratio * self.config.budget,
            self._master_compute_token,
        )

        t0 = time()
        await self.initialize_population(ecosystem=ecosystem)
        # cancel run if no agent was initialized
        if len(self.agents) == 0:
            logger.info("No agent was initialized. Exiting cycle. Check the logs for more information.")
            return []

        total_cycle_cost = ComputeIntensiveBatchProcessor.get_master_token_cost()
        logger.info(f"Initialization of {len(self.agents)} agents took {human_readable_duration(t0)}")
        logger.info(f"Budget left after initialization: {self.config.budget - ComputeIntensiveBatchProcessor.get_master_token_cost()} $")

        # running generation 0
        generation = 0
        first_generation_cost = await self.run_generation(generation)
        total_cycle_cost += first_generation_cost
        logger.info(f"Budget left after first generation: {self.config.budget - ComputeIntensiveBatchProcessor.get_master_token_cost()} $")

        # running next generations until budget is reached
        while self.config.budget - ComputeIntensiveBatchProcessor.get_master_token_cost() > first_generation_cost:
            generation += 1
            total_cycle_cost += await self.run_generation(generation)
            logger.info(f"Budget left after new generation: {self.config.budget - ComputeIntensiveBatchProcessor.get_master_token_cost()} $")


        # Evaluate last offsprings before sorting all population by fitness
        total_cycle_cost += await self._evaluate_population(generation+1)
        # TODO(xabier): this is a hack to save last evaluation
        self.save_current_state(generation+1)

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

        logger.info(f"Cycle completed in {human_readable_duration(t0)} with a total cost of {total_cycle_cost} $")
        logger.info(f"Budget left at final: {self.config.budget - ComputeIntensiveBatchProcessor.get_master_token_cost()} $")
        logger.info(f"Returning {self.config.n_best_agents_to_return} best agents")

        ComputeIntensiveBatchProcessor.release_master_token(self._master_compute_token)

        selected_agents = {
            agent.id: agent for agent in sorted_agents[:self.config.n_best_agents_to_return]
        }
        selected_fitness = {agent_id: self.agents_fitness[agent_id] for agent_id in selected_agents}
        return selected_agents, selected_fitness

    async def run_generation(self, cur_generation: int) -> float:

        logger.info(f"****** Running generation {cur_generation} ******")
        # Evaluate current population asynchronously
        logger.info(f"Evaluating current population of {len(self.agents)} agents...")
        t0 = time()
        generation_cost = await self._evaluate_population(cur_generation)
        logger.info(f"Evaluation took {human_readable_duration(t0)} for a total cost of {generation_cost} $")
        self.display_current_results()
        self.save_current_state(cur_generation)

        # Select agents for crossover and mutation
        # number of agents to be replaced
        n_replaced = int(self.config.replacement_ratio * len(self.agents))
        # number of agents to be kept
        n_kept = len(self.agents) - n_replaced
        # we randomly select the agents that will be kept
        kept_agents = self.roulette_wheel_selection(n_kept)

        # Tournament selection for crossover
        logger.info("Starting crossover and mutation...")
        selected_parent_ids_for_crossover = self.tournament_selection(n_to_select=n_replaced)
        t1 = time()
        offspring_agents, crossover_cost = await self.crossover_and_mutate(selected_parent_ids_for_crossover)
        logger.info(f"Crossover and mutation completed in {human_readable_duration(t1)} for a total cost of {crossover_cost} $")

        # we finally add kept and offspring agents
        self.agents = {agent.id: agent for agent in kept_agents.values()}
        self.agents_fitness = {agent.id: self.agents_fitness[agent.id] for agent in kept_agents.values()}
        for offspring in offspring_agents:
            self.add_agent(offspring)

        logger.info(f"Generation {cur_generation} completed in {human_readable_duration(t0)} with a total cost of {generation_cost + crossover_cost} $")

        return generation_cost + crossover_cost


    async def _evaluate_population(self, generation: int) -> float:
        tasks = []
        agent_tokens = {}
        for agent in self.agents.values():
            agent_tokens[agent.id] = ComputeIntensiveBatchProcessor.generate_token(
                self.config.budget / (len(self.agents) * 2),
                self._master_compute_token,
            )

            task = asyncio.create_task(
                self.forge.compute_fitness(agent, agent_tokens[agent.id], generation=generation),
            )
            tasks.append(task)

        results = await tqdm.gather(*tasks)

        update_first_generation_costs = (generation == 0)
        total_cost_in_dollars = 0
        for index, agent_id in enumerate(self.agents.keys()):
            fitness = results[index]
            self.agents_fitness[agent_id] = fitness
            current_agent_cost = ComputeIntensiveBatchProcessor.get_token_cost(agent_tokens[agent_id])
            total_cost_in_dollars += current_agent_cost

            if update_first_generation_costs:
                if agent_id not in self.agents_first_generation_costs:
                    self.agents_first_generation_costs[agent_id] = 0
                self.agents_first_generation_costs[agent_id] += current_agent_cost

            logger.debug(f"Agent {agent_id} fitness: {fitness}, cost: {current_agent_cost}")

        return total_cost_in_dollars


    def roulette_wheel_selection(self, num_agents_to_select: int) -> dict[str, Agent]:
        total_fitness = sum(self.agents_fitness.values())
        selected_agents = []
        agent_ids = list(self.agents_fitness.keys()).copy()
        fitness_values = list(self.agents_fitness.values()).copy()

        for _ in range(num_agents_to_select):
            pick = random.uniform(0, total_fitness)
            current = 0
            for i, fitness in enumerate(fitness_values):
                current += fitness
                if current >= pick:
                    selected_agents.append(self.agents[agent_ids[i]])
                    total_fitness -= fitness_values.pop(i)
                    agent_ids.pop(i)
                    break

        return {agent.id: agent for agent in selected_agents}

    def tournament_selection(self, n_to_select: int) -> list[str]:
        # 1. each agent participates in exactly one tournament
        # 2. the best agents of each tournament are selected
        # 3. amongst them, x% are randomly selected to replace the parents of the next generation
        # 4. the others are kept
        tournament_size = max(2, int(self.config.tournament_size_ratio * len(self.agents)))

        winning_agent_ids = []
        agents = list(self.agents.values())
        for i, agent in enumerate(agents):
            tournament_agents = [agent]
            # pick tournament_size agents at random, except the agent itself
            tournament_agents += random.sample(agents[:i] + agents[i+1:], tournament_size-1)
            tournament_fitness = [self.agents_fitness[agent.id] for agent in tournament_agents]
            best_agent = tournament_agents[tournament_fitness.index(max(tournament_fitness))]
            winning_agent_ids.append(best_agent.id)

        # WARNING: we should not select the same agent twice
        return random.choices(winning_agent_ids, k=n_to_select)

    async def crossover_and_mutate(self, selected_parent_ids: list[str]) -> tuple[list[Agent], float]:

        genetic_operator_compute_token = ComputeIntensiveBatchProcessor.generate_token(
            self.config.genetic_operator_agent_budget_ratio * self.config.budget,
            self._master_compute_token,
        )

        tasks = []
        for i in range(len(selected_parent_ids)):
            parent1_id = selected_parent_ids[i]
            parent1 = self.agents[parent1_id]
            potential_parent_ids = [_id for _id in selected_parent_ids if _id != parent1_id]
            parent2_id = random.choice(potential_parent_ids) if len(potential_parent_ids) > 0 else parent1_id
            parent2 = self.agents[parent2_id]
            genetic_operator_agent = random.choice([parent1.genetic_operator_agent, parent2.genetic_operator_agent])
            crossover_input = genetic_operator_agent.agent_engine.input_model(
                forge_description=self.forge.description,
                parent_configuration1=parent1.agent_engine.graph.model_dump(),
                parent_configuration2=parent2.agent_engine.graph.model_dump(),
                node_types=self.config.node_types,
            )

            task = crossover_agent_task(
                forge=self.forge,
                genetic_operator_agent=genetic_operator_agent,
                crossover_agent_input=crossover_input,
                crossover_agent_compute_token=genetic_operator_compute_token,
                parent1=parent1,
                parent2=parent2,
            )

            tasks.append(task)

        offsprings = await asyncio.gather(*tasks, return_exceptions=True)

        # removing None
        offsprings = [offspring for offspring in offsprings if offspring is not None]

        logger.debug(f"Number of offsprings: {len(offsprings)}/{len(selected_parent_ids)}")

        return offsprings, ComputeIntensiveBatchProcessor.get_token_cost(genetic_operator_compute_token)


    def display_current_results(self, n_best: int = 3) -> None:
        sorted_fitness = dict(sorted(self.agents_fitness.items(), key=lambda item: item[1], reverse=True))
        best_ids = list(sorted_fitness.keys())[:n_best]
        best_agents = {agent_id: self.agents[agent_id] for agent_id in best_ids}
        best_agents_fitness = {agent_id: sorted_fitness[agent_id] for agent_id in best_ids}
        self.forge.display_results(best_agents, best_agents_fitness)

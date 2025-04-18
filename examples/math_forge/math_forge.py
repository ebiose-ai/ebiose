"""Copyright (c) 2024, Inria.

Pre-release Version - DO NOT DISTRIBUTE
This software is licensed under the MIT License. See LICENSE for details.
"""

import asyncio
import csv
import random
from pathlib import Path
from typing import Literal, Self

from pydantic import BaseModel, Field, model_validator

from ebiose.core.agent import Agent
from ebiose.core.agent_forge import AgentForge


class AgentInput(BaseModel):
    math_problem: str

class AgentOutput(BaseModel):
    solution: int
    rationale: str

class MathLangGraphForge(AgentForge):
    name: str = "MathLangGraphForge"
    description: str ="Solving word math problems"
    train_csv_path: str
    test_csv_path: str
    n_problems: int | None = None

    agent_input_model: type[BaseModel] = AgentInput
    agent_output_model: type[BaseModel] = AgentOutput
    default_generated_agent_engine_type: str = "langgraph_engine"

    data: dict[str, dict] = Field(default_factory=dict, exclude=True)
    fitness: dict[str, float] = Field(default_factory=dict, exclude=True)
    current_generation: int = Field(default=0, exclude=True)
    current_problem_ids: set[str] = Field(default_factory=set, exclude=True)

    unpicked_problems: dict[str, set[str]] = Field(default_factory=dict, exclude=True)

    @model_validator(mode="after")
    def _load_data(self) -> Self:
        for name, path in zip(["train", "test"], [self.train_csv_path, self.test_csv_path], strict=True):
            with Path.open(path, "r") as csvfile:
                reader = csv.DictReader(csvfile)
                self.data[name] = {
                    row["problem_id"]: {
                        "problem": row["problem"],
                        "solution": int(row["solution"]),
                    } for row in reader
                }
        return self

    def pick_problems(self, mode: Literal["train", "test"] = "test") -> list[str]:
        # When no specific number is set, return all problems
        if self.n_problems is None:
            return list(self.data[mode].keys())

        if mode not in self.unpicked_problems or len(self.unpicked_problems[mode]) < self.n_problems:
            # Reset the pool when there aren't enough problems left
            self.unpicked_problems[mode] = list(self.data[mode].keys())
            random.shuffle(self.unpicked_problems[mode])

        # Select and remove n_problems from the pool
        selected = self.unpicked_problems[mode][:self.n_problems]
        self.unpicked_problems[mode] = self.unpicked_problems[mode][self.n_problems:]
        return selected

    async def compute_fitness(self, agent: Agent, mode: Literal["train", "test"] = "train", **kwargs: dict[str, any]) -> float:  # noqa: C901
        if agent.agent_engine.engine_type != "langgraph_engine":
            self.fitness[agent.id] = {0 for _ in range(len(self.data))}
            return 0

        generation = kwargs.get("generation", 0)
        if generation != self.current_generation or len(self.current_problem_ids) != self.n_problems:
            self.current_generation = generation
            self.current_problem_ids = self.pick_problems(mode=mode)

        tasks = []
        # pick n_problems problems randomly
        for problem_id in self.current_problem_ids:
            if agent.id in self.fitness and problem_id in self.fitness[agent.id]:
                # Use cached fitness value
                tasks.append(asyncio.sleep(0, result=self.fitness[agent.id][problem_id]))
            else:
                agent_input = self.agent_input_model(
                    math_problem=self.data[mode][problem_id]["problem"],
                )
                tasks.append(agent.run(agent_input))


        # Gather results concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Compare solutions and calculate fitness
        fitness = 0
        for idx, problem_id in enumerate(self.current_problem_ids):
            if agent.id not in self.fitness:
                self.fitness[agent.id] = {}
            if isinstance(results[idx], int): # Cached result
                fitness += results[idx]
            elif results[idx] is None:
                self.fitness[agent.id][problem_id] = 0
            elif results[idx].solution == self.data[mode][problem_id]["solution"]:
                self.fitness[agent.id][problem_id] = 1
                fitness += 1
            else:
                self.fitness[agent.id][problem_id] = 0

        if self.n_problems is not None:
            return fitness/self.n_problems

        return fitness/len(self.data[mode])



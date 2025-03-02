from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from threading import Lock
import sys

from loguru import logger

class BudgetExceededError(Exception):
    """Exception raised when a token or master budget limit is exceeded."""
    def __init__(self, message: str) -> None:
        super().__init__(message)
        logger.info(f"BudgetExceededError: {message}. Finishing process.")

@dataclass
class TokenInfo:
    limit: float
    current: float = 0.0


@dataclass
class TokenManager:
    __tokens: dict[str, TokenInfo] = field(default_factory=dict)
    __lock: Lock = field(default_factory=Lock)
    __master_token_guid: str | None = None
    __master_token_info: TokenInfo | None = None

    def acquire_master_token(self, budget: float) -> str:
        with self.__lock:
            if self.__master_token_guid is not None:
                msg = "Master token has already been retrieved"
                raise RuntimeError(msg)
            self.__master_token_guid = str(uuid.uuid4())
            self.__master_token_info = TokenInfo(limit=budget)
            return self.__master_token_guid

    def generate_token(self, limit: float, master_token: str) -> str:
        with self.__lock:
            if master_token != self.__master_token_guid:
                msg = "Master token does not match"
                raise ValueError(msg)
            token_guid = str(uuid.uuid4())
            self.__tokens[token_guid] = TokenInfo(limit=limit)
            return token_guid

    def token_exists(self, token_guid: str) -> bool:
        with self.__lock:
            return token_guid in self.__tokens

    def add_cost(self, token_guid: str, cost: float) -> None:
        with self.__lock:
            if token_guid not in self.__tokens:
                msg = f"Token guid {token_guid} not found"
                raise ValueError(msg)
            token = self.__tokens[token_guid]
            new_cost = token.current + cost
            token.current = new_cost
            new_master_cost = self.__master_token_info.current + cost
            self.__master_token_info.current = new_master_cost
            if new_cost > token.limit:
                msg = f"Token budget limit exceeded. Limit: {token.limit}, New total: {new_cost}"
                raise BudgetExceededError(msg)
            if new_master_cost > self.__master_token_info.limit:
                msg = f"Master budget limit exceeded. Limit: {self.__master_token_info.limit}, New total: {new_master_cost}"
                raise BudgetExceededError(msg)

    def get_master_token_cost(self) -> float:
        with self.__lock:
            if self.__master_token_guid is None:
                msg = "Master token has not been retrieved"
                raise RuntimeError(msg)
            return self.__master_token_info.current

    def get_token_cost(self, token_guid: str) -> float:
        with self.__lock:
            if token_guid not in self.__tokens:
                msg = f"Token guid {token_guid} not found"
                raise ValueError(msg)
            return self.__tokens[token_guid].current

    def is_token_limit_reached(self, token_guid: str) -> bool:
        with self.__lock:
            if token_guid not in self.__tokens:
                msg = f"Token guid {token_guid} not found"
                raise ValueError(msg)
            return self.__tokens[token_guid].current >= self.__tokens[token_guid].limit


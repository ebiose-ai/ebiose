"""Enums for the Ebiose system."""

from enum import Enum


class Role(int, Enum):
    """Enum for User Roles."""

    USER = 1
    ADMIN = 2


class AgentType(int, Enum):
    """Enum for Agent Types."""

    STANDARD = 0
    GENETIC_OPERATOR = 1
    ARCHITECT = 2

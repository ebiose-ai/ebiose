"""Copyright (c) 2024, Inria.

Pre-release Version - DO NOT DISTRIBUTE
This software is licensed under the MIT License. See LICENSE for details.
"""

from __future__ import annotations

from pydantic import BaseModel


class SelfUserInputModel(BaseModel):
    """Input model for the current user updating their own profile."""
    
    firstname: str | None = None
    lastname: str | None = None
    email: str | None = None
    githubId: str | None = None
    password: str | None = None


class SignupInputModel(BaseModel):
    """Input model for new user registration."""
    
    firstname: str | None = None
    lastname: str | None = None
    email: str | None = None
    githubId: str | None = None
    password: str | None = None


class UserInputModel(BaseModel):
    """Input model for creating or updating a user (admin operation)."""
    
    role: int  # Using int instead of Role enum for now
    firstname: str | None = None
    lastname: str | None = None
    email: str | None = None
    githubId: str | None = None
    creditsLimit: float
    password: str | None = None

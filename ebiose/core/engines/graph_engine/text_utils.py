"""Copyright (c) 2024, Inria.

Pre-release Version - DO NOT DISTRIBUTE
This software is licensed under the MIT License. See LICENSE for details.
"""

import re


def get_placeholders(text: str) -> list[str]:
    """Find placeholders like {math_problem} in prompts and return them with {}."""
    pattern = r"\{([^{}]+)\}"
    return re.findall(pattern, text)

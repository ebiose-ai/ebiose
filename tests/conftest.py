"""Shared pytest fixtures and configuration for all tests.

This module centralizes reusable fixtures that are used across multiple test files,
reducing duplication and improving test maintainability.

FIXTURE DEPENDENCY HIERARCHY:
============================

    basic_agent                architect_agent         genetic_operator_agent
         |                            |                          |
         +------- agent_with_relations -------+-------+
                       |
         +----------- multiple_agents (uses basic_agent in loop)
         |
         +-------+-------+-------+-------+
         |       |       |       |       |
         v       v       v       v       v
   error_recovery_scenarios  batch_operations_data  state_transition_scenarios
                             performance_stress_data  concurrent_access_data
                             failure_injection_scenarios  assertion_helpers

FIXTURE CATEGORIES:
===================
1. Basic Agents (Independent)
   - basic_agent: Minimal configuration
   - architect_agent: With agent_type
   - genetic_operator_agent: With agent_type

2. Composite Agents (Depend on Basic)
   - agent_with_relations: All relationships set
   - multiple_agents: Collection of basic agents

3. Error Handling (Depend on Agent Fixtures)
   - error_recovery_scenarios: Error patterns
   - failure_injection_scenarios: Injected failures
   - error_cases: Configuration-based errors
   - edge_case_agents: Boundary conditions

4. Batch & Performance (High-Level Scenarios)
   - batch_operations_data: Multiple configurations
   - state_transition_scenarios: State changes
   - performance_stress_data: Large-scale tests
   - concurrent_access_data: Concurrency tests

5. Helpers (Utility Fixtures)
   - assertion_helpers: Common assertions
"""

import pytest
from typing import Any, Dict, List
from ebiose.core.agent import Agent


# ============================================================================
# Test Constants
# ============================================================================

# Standard test values
TEST_AGENT_NAME = "test_agent"
TEST_AGENT_DESC = "Test agent description"

# Boundary values for stress testing
MAX_NAME_LENGTH = 10000
MAX_DESCRIPTION_LENGTH = 100000
MAX_PARENT_COUNT = 5000

# Unicode test strings
UNICODE_SAMPLES = {
    "chinese": "测试代理",
    "arabic": "وكيل الاختبار",
    "emoji": "🤖🔬🧪",
    "mixed": "Test_测试_🤖_مرحبا",
}


# ============================================================================
# Test Helper Functions
# ============================================================================

def assert_agent_has_valid_id(agent: Agent) -> None:
    """Assert agent has a properly formatted ID.
    
    Args:
        agent: Agent instance to check
        
    Raises:
        AssertionError: If ID format is invalid
    """
    assert agent.id is not None, "Agent ID should not be None"
    assert isinstance(agent.id, str), f"Agent ID should be string, got {type(agent.id)}"
    assert agent.id.startswith("agent-"), f"Agent ID should start with 'agent-', got {agent.id}"
    assert len(agent.id) > 7, f"Agent ID should have UUID suffix, got {agent.id}"


def assert_agents_unique(agents: List[Agent]) -> None:
    """Assert all agents in list have unique IDs.
    
    Args:
        agents: List of Agent instances
        
    Raises:
        AssertionError: If duplicate IDs found
    """
    ids = [agent.id for agent in agents]
    unique_ids = set(ids)
    assert len(ids) == len(unique_ids), \
        f"Found {len(ids) - len(unique_ids)} duplicate agent IDs"


def assert_agent_matches_config(agent: Agent, config: Dict[str, Any]) -> None:
    """Assert agent properties match configuration dict.
    
    Args:
        agent: Agent instance to check
        config: Configuration dictionary
        
    Raises:
        AssertionError: If any property doesn't match
    """
    for key, expected_value in config.items():
        if key == "agent_engine":
            continue  # Skip engine comparison
        actual_value = getattr(agent, key)
        assert actual_value == expected_value, \
            f"Agent.{key} = {actual_value}, expected {expected_value}"



@pytest.fixture
def assertion_helpers():
    """Fixture: Collection of assertion helper functions.
    
    Returns:
        dict: Dictionary of helper function names to functions.
    """
    return {
        "assert_valid_id": assert_agent_has_valid_id,
        "assert_unique": assert_agents_unique,
        "assert_matches_config": assert_agent_matches_config,
    }


@pytest.fixture
def test_constants():
    """Fixture: Common test constants and boundary values.
    
    Returns:
        dict: Dictionary of test constant names to values.
    """
    return {
        "max_name_length": MAX_NAME_LENGTH,
        "max_description_length": MAX_DESCRIPTION_LENGTH,
        "max_parent_count": MAX_PARENT_COUNT,
        "unicode_samples": UNICODE_SAMPLES,
    }


# ============================================================================
# Agent Fixtures
# ============================================================================


@pytest.fixture
def basic_agent():
    """Fixture: Basic agent with minimal configuration.
    
    Returns:
        Agent: An agent with just name and description.
    """
    return Agent(name="basic_agent", description="A basic test agent")


@pytest.fixture
def architect_agent():
    """Fixture: Agent with architect type.
    
    Returns:
        Agent: An agent configured as an architect.
    """
    return Agent(
        name="architect",
        description="Architect agent",
        agent_type="architect",
    )


@pytest.fixture
def genetic_operator_agent():
    """Fixture: Agent with genetic operator type.
    
    Returns:
        Agent: An agent configured as a genetic operator.
    """
    return Agent(
        name="operator",
        description="Genetic operator agent",
        agent_type="genetic_operator",
    )


@pytest.fixture
def agent_with_relations():
    """Fixture: Agent with parent, architect, and operator relations.
    
    Returns:
        Agent: A complex agent with parent IDs and role assignments.
    """
    return Agent(
        name="complex_agent",
        description="Agent with all relationships",
        parent_ids=["parent1", "parent2"],
        architect_agent_id="arch-123",
        genetic_operator_agent_id="op-456",
        agent_type="architect",
    )


@pytest.fixture
def multiple_agents(request):
    """Fixture: Create N agents with unique IDs.
    
    Supports parametrization to create variable numbers of agents.
    Usage: @pytest.mark.parametrize("multiple_agents", [3, 5, 10], indirect=True)
    
    Args:
        request: pytest request object for parametrization.
        
    Returns:
        list[Agent]: A list of unique agents.
    """
    count = getattr(request, "param", 3)
    return [Agent(name=f"agent_{i}", description=f"Agent {i}") for i in range(count)]


@pytest.fixture
def agents_collection(multiple_agents):
    """Fixture: Collection of multiple agents indexed by ID.
    
    Args:
        multiple_agents: List of agents from multiple_agents fixture.
        
    Returns:
        dict: Agents indexed by their IDs for easy lookup.
    """
    return {agent.id: agent for agent in multiple_agents}


# ============================================================================
# Configuration Fixtures
# ============================================================================


@pytest.fixture
def agent_configs():
    """Fixture: Pre-defined agent configurations for testing.
    
    Returns:
        list[dict]: List of agent configuration dictionaries.
    """
    return [
        {
            "name": "config_agent_1",
            "description": "First config agent",
            "agent_type": None,
        },
        {
            "name": "config_agent_2",
            "description": "Architect config agent",
            "agent_type": "architect",
        },
        {
            "name": "config_agent_3",
            "description": "Operator config agent",
            "agent_type": "genetic_operator",
        },
        {
            "name": "complex_config",
            "description": "Complex agent with parents",
            "parent_ids": ["p1", "p2", "p3"],
            "architect_agent_id": "arch-1",
        },
    ]


# ============================================================================
# Error Handling Fixtures
# ============================================================================


@pytest.fixture
def error_cases():
    """Fixture: Collection of error test cases with expected exceptions.
    
    Returns:
        dict: Mapping of test case names to (kwargs, expected_exception) tuples.
    """
    from pydantic_core import ValidationError
    
    return {
        "missing_name": (
            {"description": "No name provided"},
            ValidationError
        ),
        "invalid_agent_type": (
            {"name": "test", "description": "test", "agent_type": "invalid"},
            ValidationError
        ),
        "non_list_parent_ids": (
            {"name": "test", "parent_ids": "single_string"},
            (ValidationError, TypeError)
        ),
    }


@pytest.fixture
def edge_case_agents():
    """Fixture: Agents with edge case values for stress testing.
    
    Returns:
        dict: Mapping of edge case names to Agent instances.
    """
    return {
        "empty_parent_list": Agent(
            name="empty_parents",
            description="No parents",
            parent_ids=[]
        ),
        "many_parents": Agent(
            name="many_parents",
            description="Many parents",
            parent_ids=[f"parent-{i}" for i in range(50)]
        ),
        "very_long_name": Agent(
            name="a" * 5000,
            description="Long name"
        ),
        "unicode_heavy": Agent(
            name="测试 тест اختبار",
            description="多言語テキスト 다국어",
            parent_ids=["parent-🤖", "parent-🧠"]
        ),
        "special_characters": Agent(
            name="agent!@#$%^&*()",
            description="Special chars: <>?:\"{}|",
            parent_ids=["parent-@-1", "parent-#-2"]
        ),
        "all_roles_assigned": Agent(
            name="role_agent",
            description="All roles",
            architect_agent_id="arch-1",
            genetic_operator_agent_id="op-1",
            agent_type="architect",
            parent_ids=["parent-1", "parent-2"]
        ),
        "minimal_agent": Agent(name="minimal"),
    }


@pytest.fixture
def invalid_inputs():
    """Fixture: Collection of invalid inputs for boundary testing.
    
    Returns:
        dict: Mapping of invalid input categories to lists of problematic values.
    """
    return {
        "agent_types": [
            "ARCHITECT",  # Wrong case
            "Genetic_Operator",  # Wrong case
            "invalid_type",  # Not a valid type
            "architecture",  # Typo
            "genetic-operator",  # Wrong separator
        ],
        "parent_id_types": [
            None,  # None in list
            123,  # Integer in list
            [],  # Empty nested list
        ],
        "names": [
            None,  # None is invalid
            123,  # Non-string (might be coerced)
        ],
    }


# ============================================================================
# Advanced Error Scenario Fixtures
# ============================================================================


@pytest.fixture
def error_recovery_scenarios():
    """Fixture: Complex error recovery scenarios for resilience testing.
    
    Returns:
        dict: Mapping of scenario names to test data including error triggers and recovery steps.
    """
    return {
        "invalid_then_valid": {
            "invalid_kwargs": {"name": "test", "agent_type": "invalid"},
            "valid_kwargs": {"name": "recovery_test", "description": "After recovery"},
            "expected_error": "ValidationError",
        },
        "multiple_errors": {
            "attempts": [
                {"name": "test", "agent_type": "INVALID"},
                {"agent_type": "architect"},  # Missing name
                {"name": "test", "agent_type": "architect"},  # Valid
            ],
            "expected_pass_on_attempt": 2,
        },
        "boundary_then_normal": {
            "edge_case": {"name": "a" * 10000, "description": "Very long"},
            "normal_case": {"name": "normal", "description": "Regular agent"},
            "should_both_work": True,
        },
    }


@pytest.fixture
def error_message_expectations():
    """Fixture: Expected error messages for validation scenarios.
    
    Returns:
        dict: Mapping of error scenarios to expected message patterns.
    """
    return {
        "missing_name": {
            "pattern": r"(name|Field required)",
            "case_sensitive": False,
        },
        "invalid_type": {
            "pattern": r"(architect|genetic_operator|invalid)",
            "case_sensitive": True,
        },
        "invalid_parent_type": {
            "pattern": r"(string|list)",
            "case_sensitive": False,
        },
    }


@pytest.fixture
def batch_operations_data():
    """Fixture: Data for batch operation testing.
    
    Returns:
        dict: Collections of agents for batch operation testing.
    """
    return {
        "valid_agents": [
            {"name": f"valid_{i}", "description": f"Valid agent {i}"}
            for i in range(10)
        ],
        "mixed_valid_invalid": [
            {"name": "valid", "description": "Valid agent"},
            {"name": "test", "agent_type": "invalid"},  # Invalid
            {"name": "valid2", "description": "Another valid"},
            {"name": "test", "agent_type": "ARCHITECT"},  # Invalid
            {"name": "valid3", "description": "Third valid"},
        ],
        "all_invalid": [
            {"name": "test", "agent_type": "wrong1"},
            {"name": "test", "agent_type": "wrong2"},
            {"name": "test", "agent_type": "wrong3"},
        ],
    }


@pytest.fixture
def state_transition_scenarios():
    """Fixture: Agent state transition scenarios for testing state consistency.
    
    Returns:
        dict: Mapping of state transitions to test configurations.
    """
    return {
        "creation_to_modification": {
            "initial": {"name": "test", "description": "Initial"},
            "modifications": [
                {"architect_agent_id": "arch-1"},
                {"genetic_operator_agent_id": "op-1"},
                {"parent_ids": ["p1", "p2"]},
            ],
        },
        "role_transitions": {
            "base": {"name": "test", "description": "test"},
            "transitions": [
                {"agent_type": "architect"},
                {"agent_type": None},  # Reset
                {"agent_type": "genetic_operator"},
            ],
        },
        "parent_list_operations": {
            "empty": [],
            "single": ["parent-1"],
            "multiple": ["parent-1", "parent-2", "parent-3"],
            "large": [f"parent-{i}" for i in range(100)],
        },
    }


@pytest.fixture
def error_context_data():
    """Fixture: Context information for error scenarios.
    
    Returns:
        dict: Context data for various error testing scenarios.
    """
    return {
        "agent_creation_contexts": {
            "minimal": {"name": "test"},
            "complete": {
                "name": "test",
                "description": "Test agent",
                "parent_ids": ["p1", "p2"],
                "architect_agent_id": "arch-1",
                "genetic_operator_agent_id": "op-1",
                "agent_type": "architect",
            },
            "partial": {
                "name": "test",
                "description": "Partial agent",
                "parent_ids": ["p1"],
            },
        },
        "error_triggers": {
            "validation": {"name": "test", "agent_type": "invalid"},
            "missing_required": {"description": "No name"},
            "type_mismatch": {"name": "test", "parent_ids": "not_a_list"},
        },
    }


@pytest.fixture
def performance_stress_data():
    """Fixture: Data for performance and stress testing.
    
    Returns:
        dict: Stress test data with various scales.
    """
    return {
        "bulk_agent_creation": {
            "small_batch": 10,
            "medium_batch": 100,
            "large_batch": 1000,
            "huge_batch": 5000,
        },
        "large_parent_lists": {
            "small": list(range(10)),
            "medium": list(range(100)),
            "large": list(range(1000)),
            "huge": list(range(10000)),
        },
        "name_size_variations": {
            "tiny": "a",
            "small": "a" * 100,
            "medium": "a" * 1000,
            "large": "a" * 10000,
            "huge": "a" * 100000,
        },
    }


@pytest.fixture
def concurrent_access_data():
    """Fixture: Data for concurrent access testing.
    
    Returns:
        dict: Test data for concurrent operation scenarios.
    """
    return {
        "shared_resources": {
            "base_agent": Agent(name="shared", description="Shared resource"),
            "competing_modifications": [
                {"architect_agent_id": "arch-1"},
                {"genetic_operator_agent_id": "op-1"},
                {"parent_ids": ["p1"]},
            ],
        },
        "parallel_creation_count": 100,
        "concurrent_operations": [
            "create",
            "read",
            "modify",
            "delete",
        ],
    }


@pytest.fixture
def failure_injection_scenarios():
    """Fixture: Scenarios for injecting various types of failures.
    
    Returns:
        dict: Failure injection configurations.
    """
    return {
        "input_failures": {
            "null_name": {"name": None},
            "empty_string_name": {"name": ""},
            "whitespace_name": {"name": "   "},
            "invalid_type_name": {"name": 123},
        },
        "constraint_failures": {
            "invalid_agent_type": {"agent_type": "invalid"},
            "invalid_parent_ids": {"parent_ids": "not_a_list"},
            "invalid_role_id": {"architect_agent_id": 123},
        },
        "cascade_failures": {
            "chain_1": [
                {"name": "test", "agent_type": "invalid"},
                {"name": None},
                {"parent_ids": ["valid"], "agent_type": "architect"},  # Should work
            ],
            "chain_2": [
                {"agent_type": "ARCHITECT"},
                {"parent_ids": 123},
                {"name": "test", "description": "valid"},  # Should work
            ],
        },
    }


@pytest.fixture
def assertion_helpers():
    """Fixture: Helper functions for common assertions in error tests.
    
    Returns:
        dict: Mapping of assertion names to assertion functions.
    """
    def assert_valid_agent(agent):
        """Assert that an agent is valid."""
        assert agent is not None
        assert agent.id is not None
        assert agent.name is not None
        return True
    
    def assert_agent_properties(agent, **expected):
        """Assert agent properties match expected values."""
        for key, value in expected.items():
            assert getattr(agent, key) == value
        return True
    
    def assert_no_side_effects(initial_state, current_state):
        """Assert no unexpected state changes."""
        assert initial_state == current_state
        return True
    
    def assert_error_message_contains(error_str, *patterns):
        """Assert error message contains expected patterns."""
        for pattern in patterns:
            assert pattern.lower() in error_str.lower()
        return True
    
    return {
        "valid_agent": assert_valid_agent,
        "properties": assert_agent_properties,
        "no_side_effects": assert_no_side_effects,
        "error_message": assert_error_message_contains,
    }


# ============================================================================
# Pytest Configuration
# ============================================================================


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "api: mark test as API-related"
    )

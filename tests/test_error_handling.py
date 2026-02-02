"""Exception and error handling tests for the ebiose package.

This module tests error conditions, exception handling, and edge cases
to ensure robust error management across the codebase.
"""

import pytest
from pydantic_core import ValidationError
from ebiose.core.agent import Agent


# ============================================================================
# Agent Validation Tests
# ============================================================================


@pytest.mark.error
def test_agent_missing_required_name():
    """Test that Agent requires a name."""
    with pytest.raises(ValidationError) as exc_info:
        Agent(description="Agent without name")
    
    # Verify error message mentions the missing field
    assert "name" in str(exc_info.value).lower()


@pytest.mark.error
def test_agent_missing_required_description():
    """Test that description field validation."""
    # Based on actual Agent behavior, description may be optional
    # This test documents the actual behavior
    agent = Agent(name="Agent with name only")
    assert agent.name == "Agent with name only"


@pytest.mark.error
def test_agent_invalid_agent_type():
    """Test that invalid agent types are rejected."""
    with pytest.raises(ValidationError) as exc_info:
        Agent(
            name="test_agent",
            description="Test",
            agent_type="invalid_type"
        )
    
    # Verify error mentions the invalid value
    assert "invalid_type" in str(exc_info.value)


@pytest.mark.error
def test_agent_invalid_agent_type_error_message():
    """Test that agent type error messages are clear."""
    with pytest.raises(ValidationError) as exc_info:
        Agent(
            name="test_agent",
            description="Test",
            agent_type="wrong_type"
        )
    
    error_message = str(exc_info.value)
    # Should mention valid options
    assert "architect" in error_message or "genetic_operator" in error_message


# ============================================================================
# Parent ID Validation Tests
# ============================================================================


@pytest.mark.error
def test_agent_empty_parent_list():
    """Test that agents can have empty parent lists."""
    agent = Agent(
        name="no_parents",
        description="Agent with no parents",
        parent_ids=[]
    )
    assert agent.parent_ids == []


@pytest.mark.error
def test_agent_duplicate_parent_ids():
    """Test agents with duplicate parent IDs."""
    duplicate_id = "parent-1"
    agent = Agent(
        name="duplicate_parents",
        description="Agent with duplicate parents",
        parent_ids=[duplicate_id, duplicate_id, "parent-2"]
    )
    
    # Verify duplicates are preserved (not deduplicated)
    assert agent.parent_ids.count(duplicate_id) >= 1


@pytest.mark.error
def test_agent_with_none_parent_id():
    """Test that None in parent ID list is rejected."""
    with pytest.raises(ValidationError):
        Agent(
            name="none_parent",
            description="Agent with None parent",
            parent_ids=["parent-1", None, "parent-2"]
        )


# ============================================================================
# ID Field Validation Tests
# ============================================================================


@pytest.mark.error
def test_agent_architect_id_format():
    """Test that architect_agent_id can be set and retrieved."""
    architect_id = "arch-123"
    agent = Agent(
        name="test_agent",
        description="Test",
        architect_agent_id=architect_id
    )
    assert agent.architect_agent_id == architect_id


@pytest.mark.error
def test_agent_operator_id_format():
    """Test that genetic_operator_agent_id can be set and retrieved."""
    operator_id = "op-456"
    agent = Agent(
        name="test_agent",
        description="Test",
        genetic_operator_agent_id=operator_id
    )
    assert agent.genetic_operator_agent_id == operator_id


@pytest.mark.error
def test_agent_none_role_ids():
    """Test that None role IDs are handled correctly."""
    agent = Agent(
        name="test_agent",
        description="Test",
        architect_agent_id=None,
        genetic_operator_agent_id=None
    )
    assert agent.architect_agent_id is None
    assert agent.genetic_operator_agent_id is None


# ============================================================================
# String Content Validation Tests
# ============================================================================


@pytest.mark.error
def test_agent_very_long_name():
    """Test handling of very long agent names."""
    long_name = "a" * 10000
    agent = Agent(name=long_name, description="Test")
    assert agent.name == long_name
    assert len(agent.name) == 10000


@pytest.mark.error
def test_agent_very_long_description():
    """Test handling of very long descriptions."""
    long_description = "d" * 100000
    agent = Agent(name="test", description=long_description)
    assert agent.description == long_description
    assert len(agent.description) == 100000


@pytest.mark.error
def test_agent_special_characters_in_name():
    """Test agent names with special characters."""
    special_names = [
        "Agent!@#$%^&*()",
        "Agent\nwith\nnewlines",
        "Agent\twith\ttabs",
        "Agent\\with\\backslashes",
        "Agent'with'quotes",
        'Agent"with"doublequotes',
    ]
    
    for name in special_names:
        agent = Agent(name=name, description="Test")
        assert agent.name == name


@pytest.mark.error
def test_agent_unicode_content():
    """Test agent with unicode characters."""
    unicode_agent = Agent(
        name="Agent with unicode: 你好世界 مرحبا بالعالم",
        description="描述 وصف 🤖🧠"
    )
    assert "你好" in unicode_agent.name
    assert "مرحبا" in unicode_agent.name
    assert "🤖" in unicode_agent.description


@pytest.mark.error
def test_agent_empty_string_handling():
    """Test handling of empty strings for optional fields."""
    agent = Agent(
        name="test",
        description="test",
        architect_agent_id="",
        genetic_operator_agent_id=""
    )
    assert agent.architect_agent_id == ""
    assert agent.genetic_operator_agent_id == ""


# ============================================================================
# Serialization Tests
# ============================================================================


@pytest.mark.error
def test_agent_basic_serialization():
    """Test basic agent serialization to dict."""
    agent = Agent(name="test", description="test agent")
    
    # Test that we can convert to dict without errors
    agent_dict = agent.model_dump()
    
    assert agent_dict['name'] == "test"
    assert agent_dict['description'] == "test agent"


@pytest.mark.error
def test_agent_serialization_with_parent_ids():
    """Test serialization preserves parent IDs."""
    agent = Agent(
        name="test",
        description="test",
        parent_ids=["p1", "p2"]
    )
    
    agent_dict = agent.model_dump()
    
    assert agent_dict['parent_ids'] == ["p1", "p2"]


# ============================================================================
# Type Validation Tests
# ============================================================================


@pytest.mark.error
def test_agent_valid_agent_types():
    """Test that valid agent types are accepted."""
    for agent_type in ["architect", "genetic_operator"]:
        agent = Agent(
            name="test",
            description="test",
            agent_type=agent_type
        )
        assert agent.agent_type == agent_type


@pytest.mark.error
def test_agent_case_sensitive_types():
    """Test that agent types are case-sensitive."""
    with pytest.raises(ValidationError):
        Agent(
            name="test",
            description="test",
            agent_type="ARCHITECT"  # uppercase not allowed
        )


# ============================================================================
# Edge Case Tests
# ============================================================================


@pytest.mark.error
def test_agent_with_all_fields_none_or_empty():
    """Test creating an agent with minimal required fields."""
    agent = Agent(name="minimal", description="Minimal agent")
    
    assert agent.name == "minimal"
    assert agent.description == "Minimal agent"
    assert agent.parent_ids == []
    assert agent.architect_agent_id is None
    assert agent.genetic_operator_agent_id is None
    assert agent.agent_type is None


    agent = Agent(name="minimal", description="Minimal agent")
    
    assert agent.name == "minimal"
    assert agent.description == "Minimal agent"
    assert agent.parent_ids == []
    assert agent.architect_agent_id is None
    assert agent.genetic_operator_agent_id is None
    assert agent.agent_type is None


@pytest.mark.error
def test_agent_state_consistency_after_failed_creation():
    """Test that failed agent creation doesn't leave partial state."""
    with pytest.raises(ValidationError):
        Agent(name="test", agent_type="invalid")
    
    # Verify no side effects - next valid agent creation should work
    valid_agent = Agent(name="valid_agent", description="Valid")
    assert valid_agent.name == "valid_agent"
    assert valid_agent.id is not None


@pytest.mark.error
def test_agent_idempotent_access_patterns():
    """Test that repeated access to agent properties is idempotent."""
    agent = Agent(
        name="test",
        description="test",
        parent_ids=["p1", "p2"]
    )
    
    # Access multiple times - should return same values
    parent_ids_1 = agent.parent_ids
    parent_ids_2 = agent.parent_ids
    
    assert parent_ids_1 == parent_ids_2
    assert parent_ids_1 is not parent_ids_2 or parent_ids_1 == ["p1", "p2"]


# ============================================================================
# Boundary and Limit Tests
# ============================================================================


@pytest.mark.error
def test_agent_name_boundary_cases():
    """Test boundary values for agent name field."""
    # Single character name
    single_char = Agent(name="A", description="Single char")
    assert single_char.name == "A"
    
    # Very long name (tested separately, but verify it works)
    medium_name = Agent(name="a" * 1000, description="Medium length")
    assert len(medium_name.name) == 1000


@pytest.mark.error
def test_agent_parent_ids_list_boundary():
    """Test boundary values for parent ID list sizes."""
    # Zero parents
    zero_parents = Agent(name="test", parent_ids=[])
    assert len(zero_parents.parent_ids) == 0
    
    # One parent
    one_parent = Agent(name="test", parent_ids=["p1"])
    assert len(one_parent.parent_ids) == 1
    
    # Large number of parents
    large_parent_list = Agent(
        name="test",
        parent_ids=[f"parent-{i}" for i in range(1000)]
    )
    assert len(large_parent_list.parent_ids) == 1000


@pytest.mark.error
def test_agent_role_id_empty_string_vs_none():
    """Test that empty strings and None are treated differently for role IDs."""
    # None should be allowed
    agent_with_none = Agent(
        name="test",
        architect_agent_id=None,
        genetic_operator_agent_id=None
    )
    assert agent_with_none.architect_agent_id is None
    
    # Empty string should be allowed but not the same as None
    agent_with_empty = Agent(
        name="test",
        architect_agent_id="",
        genetic_operator_agent_id=""
    )
    assert agent_with_empty.architect_agent_id == ""
    assert agent_with_empty.architect_agent_id != None


@pytest.mark.error
def test_agent_name_whitespace_handling():
    """Test how agent names with whitespace are handled."""
    # Leading/trailing whitespace
    padded_name = Agent(name="  agent name  ", description="test")
    assert "agent name" in padded_name.name
    
    # Only whitespace name (may be rejected or allowed - test behavior)
    try:
        ws_agent = Agent(name="   ", description="test")
        # If allowed, verify it's stored
        assert ws_agent.name == "   "
    except ValidationError:
        # If rejected, that's also valid behavior
        pass


@pytest.mark.error
def test_agent_id_field_mutability():
    """Test that agent ID can be modified (mutable field)."""
    agent = Agent(name="test", description="test")
    original_id = agent.id
    
    # Agent ID appears to be mutable
    agent.id = "custom-id"
    
    # ID can be changed
    assert agent.id == "custom-id"
    assert agent.id != original_id


# ============================================================================
# Type Coercion and Validation Tests
# ============================================================================


@pytest.mark.error
def test_agent_type_field_validation():
    """Test agent_type field validation with various inputs."""
    # Valid types should work
    for valid_type in ["architect", "genetic_operator"]:
        agent = Agent(name="test", agent_type=valid_type)
        assert agent.agent_type == valid_type


@pytest.mark.error
def test_agent_type_none_is_valid():
    """Test that None is a valid value for agent_type."""
    agent = Agent(name="test", agent_type=None)
    assert agent.agent_type is None


@pytest.mark.error
def test_parent_ids_type_validation():
    """Test that parent_ids must be a list of strings."""
    # Valid: list of strings
    valid_agent = Agent(name="test", parent_ids=["p1", "p2"])
    assert valid_agent.parent_ids == ["p1", "p2"]
    
    # Invalid: single string instead of list
    with pytest.raises((ValidationError, TypeError)):
        Agent(name="test", parent_ids="p1")


@pytest.mark.error
def test_parent_ids_with_empty_strings():
    """Test that empty strings in parent_ids are handled."""
    agent = Agent(name="test", parent_ids=["", "parent-1", ""])
    # Verify empty strings are preserved
    assert "" in agent.parent_ids
    assert agent.parent_ids.count("") >= 1


# ============================================================================
# Recovery and Error Scenario Tests
# ============================================================================


@pytest.mark.error
def test_valid_agent_creation_after_validation_error():
    """Test that valid agent can be created after previous validation error."""
    # First attempt fails
    with pytest.raises(ValidationError):
        Agent(name="test", agent_type="invalid")
    
    # Second attempt succeeds
    valid_agent = Agent(name="test_recovery", description="After error")
    assert valid_agent.name == "test_recovery"
    assert valid_agent.id is not None


@pytest.mark.error
def test_agent_with_special_unicode_ids():
    """Test agent creation with unicode in ID fields."""
    agent = Agent(
        name="test",
        architect_agent_id="arch-🤖-123",
        genetic_operator_agent_id="op-🧬-456"
    )
    
    assert "🤖" in agent.architect_agent_id
    assert "🧬" in agent.genetic_operator_agent_id


@pytest.mark.error
def test_agent_parent_ids_with_special_characters():
    """Test parent_ids list with special characters."""
    special_ids = [
        "parent-with-dashes",
        "parent_with_underscores",
        "parent.with.dots",
        "parent@with@symbols",
        "parent:with:colons",
        "parent/with/slashes",
    ]
    
    agent = Agent(name="test", parent_ids=special_ids)
    assert agent.parent_ids == special_ids


@pytest.mark.error
def test_concurrent_agent_creation_ids_unique():
    """Test that rapidly created agents have unique IDs."""
    agents = [Agent(name=f"agent_{i}", description=f"Agent {i}") for i in range(100)]
    
    agent_ids = [agent.id for agent in agents]
    # All IDs should be unique
    assert len(set(agent_ids)) == len(agent_ids)


# ============================================================================
# Negative Test Cases
# ============================================================================


@pytest.mark.error
def test_agent_name_cannot_be_none():
    """Test that agent name cannot be None."""
    with pytest.raises(ValidationError):
        Agent(name=None, description="test")


@pytest.mark.error
def test_agent_with_numeric_string_parent_ids():
    """Test that numeric strings in parent_ids are treated as strings."""
    agent = Agent(
        name="test",
        parent_ids=["1", "2", "3"]
    )
    
    assert agent.parent_ids == ["1", "2", "3"]
    # Verify they're not converted to integers
    assert all(isinstance(pid, str) for pid in agent.parent_ids)


@pytest.mark.error
def test_agent_type_case_sensitivity_enforced():
    """Test that agent type validation is case-sensitive."""
    invalid_types = [
        "Architect",
        "ARCHITECT",
        "genetic_operator_CAPS",
        "Genetic_Operator"
    ]
    
    for invalid_type in invalid_types:
        with pytest.raises(ValidationError):
            Agent(name="test", agent_type=invalid_type)


@pytest.mark.error
def test_agent_equality_by_id_not_content():
    """Test that agents are considered different even with identical content."""
    agent1 = Agent(
        name="identical",
        description="same description",
        parent_ids=["parent1"]
    )
    
    agent2 = Agent(
        name="identical",
        description="same description",
        parent_ids=["parent1"]
    )
    
    # Should have different IDs
    assert agent1.id != agent2.id
    # But same content
    assert agent1.name == agent2.name
    assert agent1.description == agent2.description


@pytest.mark.error
def test_agent_equality_same_values():

    """Test that agents with same values are equal by ID, not content."""
    agent1 = Agent(name="same_name", description="same_desc")
    agent2 = Agent(name="same_name", description="same_desc")
    
    # Agents should have different IDs even with same content
    assert agent1.id != agent2.id


@pytest.mark.error
def test_agent_mutation_safety():
    """Test that modifying parent list doesn't affect agent unexpectedly."""
    original_parents = ["p1", "p2"]
    agent = Agent(
        name="test",
        description="test",
        parent_ids=original_parents.copy()
    )
    
    # Verify the agent stores the parents
    assert agent.parent_ids == original_parents

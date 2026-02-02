"""Advanced error handling and edge case tests using fixtures.

This module extends basic error handling tests with fixture-based parametrized tests
for comprehensive coverage of boundary conditions and error scenarios.
"""

import pytest
from pydantic_core import ValidationError
from ebiose.core.agent import Agent


# ============================================================================
# Fixture-Based Error Case Tests
# ============================================================================


@pytest.mark.error
def test_error_cases_with_fixture(error_cases):
    """Test documented error cases."""
    for case_name, (kwargs, expected_exc) in error_cases.items():
        with pytest.raises(expected_exc):
            Agent(**kwargs)


@pytest.mark.error
def test_edge_case_agents_all_valid(edge_case_agents):
    """Test that all edge case agent fixtures are valid."""
    for case_name, agent in edge_case_agents.items():
        assert agent is not None
        assert agent.id is not None
        assert agent.name is not None


@pytest.mark.error
def test_edge_case_agents_properties(edge_case_agents):
    """Test specific properties of edge case agents."""
    # Many parents case
    assert len(edge_case_agents["many_parents"].parent_ids) == 50
    
    # Very long name case
    assert len(edge_case_agents["very_long_name"].name) == 5000
    
    # Unicode heavy case
    assert "测试" in edge_case_agents["unicode_heavy"].name
    assert "🤖" in edge_case_agents["unicode_heavy"].parent_ids[0]
    
    # All roles assigned case
    assert edge_case_agents["all_roles_assigned"].architect_agent_id == "arch-1"
    assert edge_case_agents["all_roles_assigned"].genetic_operator_agent_id == "op-1"
    
    # Minimal agent case
    assert edge_case_agents["minimal_agent"].name == "minimal"


@pytest.mark.error
def test_invalid_agent_types_with_fixture(invalid_inputs):
    """Test that all invalid agent types are rejected."""
    for invalid_type in invalid_inputs["agent_types"]:
        with pytest.raises(ValidationError):
            Agent(name="test", agent_type=invalid_type)


# ============================================================================
# Parametrized Boundary Tests
# ============================================================================


@pytest.mark.error
@pytest.mark.parametrize(
    "parent_count", 
    [0, 1, 10, 100, 500, 1000],
    ids=lambda x: f"parents_{x}"
)
def test_agent_with_varying_parent_counts(parent_count):
    """Test agent creation with various parent list sizes."""
    parents = [f"parent-{i}" for i in range(parent_count)]
    agent = Agent(name=f"agent_{parent_count}", parent_ids=parents)
    
    assert len(agent.parent_ids) == parent_count
    assert agent.parent_ids == parents


@pytest.mark.error
@pytest.mark.parametrize(
    "name_length", 
    [1, 10, 100, 1000, 10000],
    ids=lambda x: f"len_{x}"
)
def test_agent_with_varying_name_lengths(name_length):
    """Test agent creation with various name lengths."""
    name = "a" * name_length
    agent = Agent(name=name, description="test")
    
    assert len(agent.name) == name_length
    assert agent.name == name


@pytest.mark.error
@pytest.mark.parametrize(
    "description_length", 
    [0, 1, 100, 1000, 10000, 100000],
    ids=lambda x: f"len_{x}"
)
def test_agent_with_varying_description_lengths(description_length):
    """Test agent creation with various description lengths."""
    description = "d" * description_length
    agent = Agent(name="test", description=description)
    
    assert len(agent.description) == description_length


@pytest.mark.parametrize("unicode_text", [
    "Hello World",
    "你好世界",
    "مرحبا بالعالم",
    "Привет мир",
    "🤖🧠🔥⚡✨",
    "Mixed: Hello 你好 مرحبا Привет",
])
@pytest.mark.error
def test_agent_with_unicode_names(unicode_text):
    """Test agent creation with various unicode text."""
    agent = Agent(name=unicode_text, description="unicode test")
    assert agent.name == unicode_text


@pytest.mark.parametrize("special_chars", [
    "!@#$%^&*()",
    "<>?:\"{}|",
    "[]\\;',./-=",
    "\n\t\r",
    "test-with-dashes",
    "test_with_underscores",
    "test.with.dots",
])
@pytest.mark.error
def test_agent_with_special_characters(special_chars):
    """Test agent creation with special characters in name."""
    agent = Agent(name=f"agent{special_chars}", description="test")
    assert special_chars in agent.name


@pytest.mark.parametrize("valid_agent_type", [None, "architect", "genetic_operator"])
def test_agent_valid_types_only(valid_agent_type):
    """Test that only valid agent types are accepted."""
    agent = Agent(name="test", agent_type=valid_agent_type)
    assert agent.agent_type == valid_agent_type


@pytest.mark.parametrize("role_id,description", [
    (None, "None role ID"),
    ("", "Empty string role ID"),
    ("role-123", "Standard role ID"),
    ("role-with-🤖", "Unicode role ID"),
    ("role/with/special", "Special char role ID"),
])
@pytest.mark.error
def test_agent_role_id_variations(role_id, description):
    """Test various role ID formats."""
    agent = Agent(
        name="test",
        architect_agent_id=role_id,
        description=description
    )
    assert agent.architect_agent_id == role_id


# ============================================================================
# Recovery and Resilience Tests
# ============================================================================


@pytest.mark.error
def test_agent_creation_resilience(edge_case_agents):
    """Test that edge case agents can be created repeatedly."""
    for _ in range(5):
        for case_name, template_agent in edge_case_agents.items():
            # Create new agent with same properties
            new_agent = Agent(
                name=template_agent.name,
                parent_ids=template_agent.parent_ids,
                architect_agent_id=template_agent.architect_agent_id
            )
            
            assert new_agent.id != template_agent.id  # Different IDs
            assert new_agent.name == template_agent.name  # Same content


@pytest.mark.error
def test_invalid_then_valid_agent_creation(invalid_inputs):
    """Test that valid agent creation works after invalid attempts."""
    # Try invalid types
    for invalid_type in invalid_inputs["agent_types"][:3]:
        with pytest.raises(ValidationError):
            Agent(name="test", agent_type=invalid_type)
    
    # Should still be able to create valid agent
    valid_agent = Agent(name="valid", description="test", agent_type="architect")
    assert valid_agent.agent_type == "architect"


# ============================================================================
# Constraint Violation Tests
# ============================================================================


@pytest.mark.error
def test_agent_id_uniqueness_with_many_agents():
    """Test that many agents have unique IDs."""
    agents = [Agent(name=f"agent_{i}") for i in range(1000)]
    ids = [agent.id for agent in agents]
    
    # All IDs should be unique
    assert len(set(ids)) == len(ids)
    assert len(ids) == 1000


@pytest.mark.error
def test_agent_mutability_of_id():
    """Test that agent ID can be modified after creation."""
    agent = Agent(name="test")
    original_id = agent.id
    
    # Agent ID is mutable
    agent.id = "new_id"
    
    # ID was successfully changed
    assert agent.id == "new_id"
    assert agent.id != original_id


@pytest.mark.error
def test_parent_ids_independence():
    """Test that parent_ids list is independent between agents."""
    parents1 = ["p1", "p2"]
    parents2 = ["p3", "p4"]
    
    agent1 = Agent(name="agent1", parent_ids=parents1)
    agent2 = Agent(name="agent2", parent_ids=parents2)
    
    # Verify they're independent
    assert agent1.parent_ids != agent2.parent_ids
    assert agent1.parent_ids == parents1
    assert agent2.parent_ids == parents2


# ============================================================================
# Error Message Quality Tests
# ============================================================================


@pytest.mark.error
def test_error_message_clarity_missing_required_field():
    """Test that error messages clearly indicate missing required fields."""
    with pytest.raises(ValidationError) as exc_info:
        Agent()
    
    error_str = str(exc_info.value)
    # Should mention what field(s) are missing
    assert "name" in error_str.lower() or "field" in error_str.lower()


@pytest.mark.error
def test_error_message_clarity_invalid_type():
    """Test that error messages clearly indicate type issues."""
    with pytest.raises(ValidationError) as exc_info:
        Agent(name="test", agent_type="invalid_option")
    
    error_str = str(exc_info.value)
    # Should mention the invalid value
    assert "invalid_option" in error_str


@pytest.mark.error
def test_error_message_includes_constraints():
    """Test that error messages mention constraints."""
    with pytest.raises(ValidationError) as exc_info:
        Agent(name="test", agent_type="ARCHITECT")  # Wrong case
    
    error_str = str(exc_info.value)
    # Should help user understand valid options
    assert "architect" in error_str or "genetic_operator" in error_str


# ============================================================================
# Concurrency and Race Condition Tests
# ============================================================================


@pytest.mark.error
def test_agent_ids_collision_resistance():
    """Test that agent ID generation resists collisions."""
    # Create many agents and check for ID collisions
    agents = [Agent(name=f"agent_{i}") for i in range(500)]
    ids = [a.id for a in agents]
    
    # No duplicate IDs
    assert len(ids) == len(set(ids))


@pytest.mark.parametrize("iteration", range(10))
def test_repeated_agent_creation_consistency(iteration):
    """Test that repeated agent creation is consistent."""
    agent1 = Agent(
        name="consistency_test",
        description="Test consistency",
        parent_ids=["p1", "p2"],
        agent_type="architect"
    )
    
    agent2 = Agent(
        name="consistency_test",
        description="Test consistency",
        parent_ids=["p1", "p2"],
        agent_type="architect"
    )
    
    # Same properties but different IDs
    assert agent1.name == agent2.name
    assert agent1.description == agent2.description
    assert agent1.parent_ids == agent2.parent_ids
    assert agent1.agent_type == agent2.agent_type
    assert agent1.id != agent2.id


# ============================================================================
# Defensive Programming Tests
# ============================================================================


@pytest.mark.error
def test_agent_against_null_injection():
    """Test that null/None values are handled safely."""
    # Null in parent_ids should be rejected
    with pytest.raises(ValidationError):
        Agent(name="test", parent_ids=[None, "valid_parent"])


@pytest.mark.error
def test_agent_against_empty_list_parent_ids():
    """Test that empty parent list is valid but different from missing."""
    agent_empty = Agent(name="test", parent_ids=[])
    agent_default = Agent(name="test")
    
    # Both should have empty parent lists
    assert agent_empty.parent_ids == []
    assert agent_default.parent_ids == []


@pytest.mark.error
def test_agent_type_normalization_not_applied():
    """Test that agent type is not automatically normalized."""
    # Uppercase should be rejected, not normalized
    with pytest.raises(ValidationError):
        Agent(name="test", agent_type="ARCHITECT")

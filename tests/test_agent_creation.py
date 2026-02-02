"""Integration tests for agent creation and factory.

This module tests the Agent class and factory pattern for creating agents with
various configurations, including type variants, parent relationships, serialization,
and edge cases.
"""

import pytest
from pydantic import BaseModel

from ebiose.core.agent import Agent


# ============================================================================
# Parametrized Tests
# ============================================================================


@pytest.mark.unit
@pytest.mark.parametrize(
    "name,description,agent_type",
    [
        ("agent1", "Test agent 1", None),
        ("agent2", "Test agent 2", "architect"),
        ("agent3", "Test agent 3", "genetic_operator"),
        ("special-agent_123", "Agent with special chars", None),
    ],
    ids=["basic", "architect", "operator", "special-chars"]
)
def test_agent_initialization_with_variants(name, description, agent_type):
    """Test agent initialization with various configurations."""
    agent = Agent(name=name, description=description, agent_type=agent_type)

    assert agent.name == name
    assert agent.description == description
    assert agent.agent_type == agent_type
    assert agent.id is not None
    assert agent.id.startswith("agent-")


@pytest.mark.unit
@pytest.mark.parametrize(
    "parent_count",
    [0, 1, 2, 5, 10, 50, 100],
    ids=lambda x: f"parents_{x}"
)
def test_agent_parent_list_sizes(parent_count):
    """Test agent with varying parent list sizes."""
    parent_ids = [f"parent-{i}" for i in range(parent_count)]
    agent = Agent(name="test", description="Test", parent_ids=parent_ids)

    assert len(agent.parent_ids) == parent_count
    assert agent.parent_ids == parent_ids


@pytest.mark.unit
@pytest.mark.parametrize(
    "agent_type",
    [None, "architect", "genetic_operator"],
    ids=["none", "architect", "operator"]
)
def test_agent_type_variants(agent_type):
    """Test all valid agent type values."""
    agent = Agent(name="test", description="Test", agent_type=agent_type)
    assert agent.agent_type == agent_type


@pytest.mark.unit
@pytest.mark.parametrize(
    "name",
    [
        "simple",
        "with-dashes",
        "with_underscores",
        "with numbers 123",
        "with special !@#$%",
        "unicode_🤖_智能",
        "a" * 500,  # Very long name
    ],
    ids=["simple", "dashes", "underscores", "numbers", "special", "unicode", "long-500"]
)
def test_agent_name_variations(name):
    """Test agent creation with various name formats."""
    agent = Agent(name=name, description="Test")
    assert agent.name == name


@pytest.mark.unit
@pytest.mark.parametrize(
    "description",
    [
        "Simple description",
        "Description with\nmultiple\nlines",
        "Unicode: 你好 مرحبا 🤖",
        "d" * 1000,  # Very long description
        "",  # Empty description
    ],
    ids=["simple", "multiline", "unicode", "long-1000", "empty"]
)
def test_agent_description_variations(description):
    """Test agent creation with various description formats."""
    agent = Agent(name="test", description=description)
    assert agent.description == description


@pytest.mark.parametrize(
    "arch_id,op_id",
    [
        (None, None),
        ("arch-1", None),
        (None, "op-1"),
        ("arch-123", "op-456"),
        ("12345", "67890"),  # Numeric IDs
        ("550e8400-e29b-41d4-a716-446655440000", "550e8400-e29b-41d4-a716-446655440001"),  # UUID style
    ],
)
@pytest.mark.unit
def test_agent_id_combinations(arch_id, op_id):
    """Test agent with various architect and operator ID combinations."""
    agent = Agent(
        name="test",
        description="Test",
        architect_agent_id=arch_id,
        genetic_operator_agent_id=op_id,
    )

    assert agent.architect_agent_id == arch_id
    assert agent.genetic_operator_agent_id == op_id


# ============================================================================
# Fixture-based Tests
# ============================================================================


@pytest.mark.unit
def test_basic_agent_fixture(basic_agent):
    """Test fixture-created basic agent."""
    assert basic_agent.name == "basic_agent"
    assert basic_agent.description == "A basic test agent"
    assert basic_agent.id is not None
    assert basic_agent.agent_type is None


@pytest.mark.unit
def test_architect_agent_fixture(architect_agent):
    """Test fixture-created architect agent."""
    assert architect_agent.agent_type == "architect"
    assert architect_agent.name == "architect"


@pytest.mark.unit
def test_genetic_operator_agent_fixture(genetic_operator_agent):
    """Test fixture-created genetic operator agent."""
    assert genetic_operator_agent.agent_type == "genetic_operator"
    assert genetic_operator_agent.name == "operator"


@pytest.mark.integration
def test_agent_with_relations_fixture(agent_with_relations):
    """Test fixture-created agent with all relationships."""
    assert agent_with_relations.parent_ids == ["parent1", "parent2"]
    assert agent_with_relations.architect_agent_id == "arch-123"
    assert agent_with_relations.genetic_operator_agent_id == "op-456"
    assert agent_with_relations.agent_type == "architect"


@pytest.mark.unit
def test_agent_serialization(agent_with_relations):
    """Test agent serialization using fixture."""
    serialized = agent_with_relations.model_dump(mode="json", exclude={"agent_engine"})

    assert serialized["name"] == "complex_agent"
    assert serialized["description"] == "Agent with all relationships"
    assert serialized["parent_ids"] == ["parent1", "parent2"]
    assert serialized["architect_agent_id"] == "arch-123"
    assert serialized["genetic_operator_agent_id"] == "op-456"


@pytest.mark.unit
@pytest.mark.parametrize("count", [3, 5, 10, 100], ids=lambda x: f"count_{x}")
def test_multiple_agents_uniqueness(count):
    """Test that creating multiple agents results in unique IDs."""
    agents = [Agent(name=f"agent_{i}", description=f"Agent {i}") for i in range(count)]
    ids = [agent.id for agent in agents]

    # All IDs should be unique
    assert len(ids) == len(set(ids))


@pytest.mark.unit
def test_agents_fixture_uniqueness(multiple_agents):
    """Test uniqueness using fixture with parametrization."""
    ids = [agent.id for agent in multiple_agents]
    assert len(ids) == len(set(ids))


# ============================================================================
# Integration Tests using Fixtures
# ============================================================================


@pytest.mark.integration
def test_agent_dict_roundtrip(agent_with_relations):
    """Test serialization and data preservation."""
    serialized = agent_with_relations.model_dump(mode="json", exclude={"agent_engine"})

    # Verify critical fields are present
    assert all(
        key in serialized
        for key in [
            "name",
            "description",
            "id",
            "parent_ids",
            "architect_agent_id",
            "genetic_operator_agent_id",
            "agent_type",
        ]
    )


@pytest.mark.integration
def test_agent_collection_by_id(multiple_agents):
    """Test storing agents in dict by ID (like forge cycle does)."""
    agent_dict = {agent.id: agent for agent in multiple_agents}

    assert len(agent_dict) == len(multiple_agents)

    # All agents should be retrievable by ID
    for agent in multiple_agents:
        assert agent_dict[agent.id].id == agent.id


@pytest.mark.parametrize("count", [1, 10, 100])
def test_large_parent_list_with_agents(count):
    """Test agent with large parent lists."""
    parent_ids = [f"parent-{i}" for i in range(count)]
    agent = Agent(name="test", description="Test", parent_ids=parent_ids)

    assert len(agent.parent_ids) == count
    assert all(f"parent-{i}" in agent.parent_ids for i in range(count))


@pytest.mark.parametrize(
    "agent_config",
    [
        {"name": "a1", "description": "desc1"},
        {"name": "a2", "description": "desc2", "agent_type": "architect"},
        {"name": "a3", "description": "desc3", "parent_ids": ["p1", "p2"]},
        {
            "name": "a4",
            "description": "desc4",
            "agent_type": "genetic_operator",
            "architect_agent_id": "arch-1",
            "genetic_operator_agent_id": "op-1",
            "parent_ids": ["p1", "p2", "p3"],
        },
    ],
)
@pytest.mark.unit
def test_agent_creation_from_configs(agent_config):
    """Test agent creation from various configurations."""
    agent = Agent(**agent_config)

    # Verify name and description are always set
    assert agent.name == agent_config["name"]
    assert agent.description == agent_config["description"]

    # Verify optional fields
    if "agent_type" in agent_config:
        assert agent.agent_type == agent_config["agent_type"]
    if "parent_ids" in agent_config:
        assert agent.parent_ids == agent_config["parent_ids"]
    if "architect_agent_id" in agent_config:
        assert agent.architect_agent_id == agent_config["architect_agent_id"]
    if "genetic_operator_agent_id" in agent_config:
        assert agent.genetic_operator_agent_id == agent_config["genetic_operator_agent_id"]


# ============================================================================
# Boundary and Edge Case Tests
# ============================================================================


@pytest.mark.parametrize(
    "duplicate_parent",
    [
        ["p1", "p1"],
        ["p1", "p2", "p1"],
        ["p1"] * 10,
    ],
)
@pytest.mark.unit
def test_agent_duplicate_parent_preservation(duplicate_parent):
    """Test that duplicate parent IDs are preserved (not deduplicated)."""
    agent = Agent(name="test", description="Test", parent_ids=duplicate_parent)
    assert agent.parent_ids == duplicate_parent
    assert agent.parent_ids.count("p1") == duplicate_parent.count("p1")


@pytest.mark.unit
def test_agent_empty_parent_list():
    """Test agent with explicitly empty parent list."""
    agent = Agent(name="orphan", description="No parents", parent_ids=[])
    assert agent.parent_ids == []
    assert len(agent.parent_ids) == 0


@pytest.mark.unit
def test_agent_id_format_consistency(multiple_agents):
    """Test all agent IDs follow expected format."""
    for agent in multiple_agents:
        assert agent.id.startswith("agent-")
        assert len(agent.id) > len("agent-")  # Has UUID part
        assert len(agent.id.split("-")) >= 2  # Has UUID segments


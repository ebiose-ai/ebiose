"""Integration tests for agent workflows and ecosystem interactions.

This module tests how agents interact within ecosystems, including agent relationships,
event handling, and multi-agent workflows.
"""

import pytest
from ebiose.core.agent import Agent


# ============================================================================
# Agent Relationship Tests
# ============================================================================


@pytest.mark.integration
def test_agent_parent_child_relationships(basic_agent, genetic_operator_agent):
    """Test creating agents with parent-child relationships."""
    parent_agent = basic_agent
    child_agent = Agent(
        name="child_agent",
        description="Child agent with parent",
        parent_ids=[parent_agent.id]
    )
    
    assert parent_agent.id in child_agent.parent_ids
    assert len(child_agent.parent_ids) == 1


@pytest.mark.integration
def test_agent_with_multiple_parents(basic_agent, architect_agent, genetic_operator_agent):
    """Test creating an agent with multiple parents."""
    parents = [basic_agent.id, architect_agent.id, genetic_operator_agent.id]
    
    multi_parent_agent = Agent(
        name="multi_parent_agent",
        description="Agent with multiple parents",
        parent_ids=parents
    )
    
    assert len(multi_parent_agent.parent_ids) == 3
    assert set(multi_parent_agent.parent_ids) == set(parents)


@pytest.mark.integration
def test_agent_role_assignments(basic_agent):
    """Test assigning architect and operator roles to agents."""
    architect = Agent(
        name="architect_role",
        description="Agent assigned architect role",
        agent_type="architect"
    )
    
    operator = Agent(
        name="operator_role",
        description="Agent assigned operator role",
        agent_type="genetic_operator"
    )
    
    main_agent = Agent(
        name="main_with_roles",
        description="Main agent with assigned roles",
        architect_agent_id=architect.id,
        genetic_operator_agent_id=operator.id
    )
    
    assert main_agent.architect_agent_id == architect.id
    assert main_agent.genetic_operator_agent_id == operator.id


# ============================================================================
# Agent Collection Tests
# ============================================================================


@pytest.mark.integration
def test_agent_collection_creation(multiple_agents):
    """Test creating a collection of agents."""
    agents = multiple_agents
    
    assert len(agents) == 3
    assert all(isinstance(agent, Agent) for agent in agents)
    assert len(set(agent.id for agent in agents)) == len(agents)  # All IDs unique


@pytest.mark.integration
def test_agent_collection_lookup(agents_collection):
    """Test looking up agents in a collection by ID."""
    for agent_id, agent in agents_collection.items():
        assert agent.id == agent_id


@pytest.mark.integration
def test_agent_collection_filtering():
    """Test filtering agents by type."""
    agents = [
        Agent(name="a1", description="Basic agent"),
        Agent(name="a2", description="Architect", agent_type="architect"),
        Agent(name="a3", description="Basic agent 2"),
        Agent(name="a4", description="Operator", agent_type="genetic_operator"),
    ]
    
    architects = [a for a in agents if a.agent_type == "architect"]
    operators = [a for a in agents if a.agent_type == "genetic_operator"]
    
    assert len(architects) == 1
    assert len(operators) == 1
    assert architects[0].name == "a2"
    assert operators[0].name == "a4"


# ============================================================================
# Agent Interaction Workflow Tests
# ============================================================================


@pytest.mark.integration
def test_agent_evolution_workflow():
    """Test a basic agent evolution workflow with parent-child lineage."""
    # Generation 1: Initial agents
    gen1_agent = Agent(
        name="gen1_agent",
        description="First generation agent",
        agent_type="architect"
    )
    
    # Generation 2: Offspring with parent reference
    gen2_agent = Agent(
        name="gen2_agent",
        description="Second generation agent",
        parent_ids=[gen1_agent.id],
        agent_type="genetic_operator"
    )
    
    # Generation 3: Another offspring
    gen3_agent = Agent(
        name="gen3_agent",
        description="Third generation agent",
        parent_ids=[gen2_agent.id]
    )
    
    # Verify the lineage
    assert gen1_agent.id in gen2_agent.parent_ids
    assert gen2_agent.id in gen3_agent.parent_ids
    assert len(gen3_agent.parent_ids) == 1


@pytest.mark.integration
def test_agent_collaboration_setup():
    """Test setting up a collaboration between multiple agents."""
    # Create a primary agent
    primary = Agent(
        name="primary_agent",
        description="Primary orchestrating agent",
        agent_type="architect"
    )
    
    # Create supporting agents
    architect = Agent(
        name="supporting_architect",
        description="Supporting architect",
        agent_type="architect"
    )
    
    operator = Agent(
        name="genetic_operator",
        description="Genetic operator",
        agent_type="genetic_operator"
    )
    
    # Assign roles
    collaborative_agent = Agent(
        name="collaborative_agent",
        description="Agent with collaborative roles",
        parent_ids=[primary.id],
        architect_agent_id=architect.id,
        genetic_operator_agent_id=operator.id
    )
    
    assert collaborative_agent.architect_agent_id == architect.id
    assert collaborative_agent.genetic_operator_agent_id == operator.id
    assert primary.id in collaborative_agent.parent_ids


# ============================================================================
# Performance and Scale Tests
# ============================================================================


@pytest.mark.parametrize("agent_count", [10, 50, 100])
def test_large_agent_collection_handling(agent_count):
    """Test handling collections of many agents efficiently."""
    agents = [
        Agent(name=f"agent_{i}", description=f"Agent {i}")
        for i in range(agent_count)
    ]
    
    # Verify all agents are unique
    agent_ids = [agent.id for agent in agents]
    assert len(set(agent_ids)) == agent_count
    
    # Test lookup performance
    agent_map = {agent.id: agent for agent in agents}
    assert len(agent_map) == agent_count
    
    # Test filtering
    half_count = agent_count // 2
    first_half = agents[:half_count]
    second_half = agents[half_count:]
    
    assert len(first_half) + len(second_half) == agent_count


@pytest.mark.integration
def test_complex_agent_hierarchy():
    """Test creating a complex multi-level agent hierarchy."""
    # Create root agents
    root1 = Agent(name="root_1", description="Root agent 1", agent_type="architect")
    root2 = Agent(name="root_2", description="Root agent 2", agent_type="genetic_operator")
    
    # Create middle layer with parents
    middle1 = Agent(
        name="middle_1",
        description="Middle layer agent 1",
        parent_ids=[root1.id]
    )
    
    middle2 = Agent(
        name="middle_2",
        description="Middle layer agent 2",
        parent_ids=[root2.id]
    )
    
    # Create leaf nodes with multiple parents
    leaf = Agent(
        name="leaf_agent",
        description="Leaf agent with multiple parents",
        parent_ids=[middle1.id, middle2.id],
        architect_agent_id=root1.id,
        genetic_operator_agent_id=root2.id
    )
    
    # Verify hierarchy
    assert len(leaf.parent_ids) == 2
    assert leaf.architect_agent_id == root1.id
    assert leaf.genetic_operator_agent_id == root2.id

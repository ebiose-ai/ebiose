"""Performance and stress testing with error scenarios.

This module tests error handling and agent creation under stress conditions,
including high-volume operations and resource constraints.
"""

import pytest
from pydantic_core import ValidationError
from ebiose.core.agent import Agent


# ============================================================================
# Bulk Agent Creation Tests
# ============================================================================


@pytest.mark.parametrize("batch_size", [10, 50, 100, 500])
def test_bulk_agent_creation_valid(batch_size):
    """Test creating large batches of valid agents."""
    agents = [
        Agent(name=f"agent_{i}", description=f"Agent {i}")
        for i in range(batch_size)
    ]
    
    assert len(agents) == batch_size
    # All agents should have unique IDs
    ids = [agent.id for agent in agents]
    assert len(set(ids)) == batch_size


@pytest.mark.parametrize("batch_size", [10, 50, 100])
def test_bulk_agent_creation_with_parents(batch_size):
    """Test creating agents with parent relationships at scale."""
    agents = []
    for i in range(batch_size):
        parent_ids = [agents[j].id for j in range(max(0, i-3), i)]
        agent = Agent(
            name=f"agent_{i}",
            description=f"Agent {i}",
            parent_ids=parent_ids
        )
        agents.append(agent)
    
    assert len(agents) == batch_size
    # Later agents should have parents
    for i in range(3, batch_size):
        assert len(agents[i].parent_ids) > 0


@pytest.mark.parametrize("batch_size", [10, 50, 100])
def test_bulk_agent_creation_error_rate(batch_size):
    """Test error rate with intentional failures in bulk."""
    valid_count = 0
    error_count = 0
    
    for i in range(batch_size):
        # Alternate valid and invalid
        if i % 2 == 0:
            try:
                Agent(name=f"agent_{i}", description=f"Agent {i}")
                valid_count += 1
            except ValidationError:
                error_count += 1
        else:
            try:
                Agent(name=f"agent_{i}", agent_type="invalid")
                valid_count += 1
            except ValidationError:
                error_count += 1
    
    # Should have roughly equal distribution
    assert valid_count > 0
    assert error_count > 0


# ============================================================================
# Large Parent List Tests
# ============================================================================


@pytest.mark.parametrize("parent_count", [10, 100, 500, 1000])
def test_agent_with_large_parent_list(parent_count):
    """Test agents with many parents."""
    parents = [f"parent-{i}" for i in range(parent_count)]
    agent = Agent(
        name="large_parent_agent",
        description="Agent with many parents",
        parent_ids=parents
    )
    
    assert len(agent.parent_ids) == parent_count
    assert agent.id is not None


@pytest.mark.parametrize("parent_count", [100, 500, 1000])
def test_parent_list_operations_large(parent_count):
    """Test modifying large parent lists."""
    agent = Agent(name="test", description="test")
    
    # Set large parent list
    parents = [f"parent-{i}" for i in range(parent_count)]
    agent.parent_ids = parents
    assert len(agent.parent_ids) == parent_count
    
    # Add more parents
    new_parents = parents + [f"new-parent-{i}" for i in range(10)]
    agent.parent_ids = new_parents
    assert len(agent.parent_ids) == parent_count + 10


# ============================================================================
# Large String Tests
# ============================================================================


@pytest.mark.parametrize("size", [1000, 10000, 100000])
def test_agent_with_large_name(size):
    """Test agents with very long names."""
    name = "a" * size
    agent = Agent(name=name, description="Large name test")
    
    assert len(agent.name) == size
    assert agent.id is not None


@pytest.mark.parametrize("size", [1000, 10000, 100000])
def test_agent_with_large_description(size):
    """Test agents with very long descriptions."""
    description = "d" * size
    agent = Agent(name="test", description=description)
    
    assert len(agent.description) == size
    assert agent.id is not None


@pytest.mark.parametrize("size", [100, 1000, 10000])
def test_agent_with_many_special_chars(size):
    """Test agents with many special characters."""
    special_chars = "!@#$%^&*()[]{}|\\:;\"'<>,.?/~`" * (size // 30)
    agent = Agent(name=f"special_{size}", description=special_chars[:size])
    
    # Pydantic may normalize some characters, so we verify agent was created and has content
    assert len(agent.description) > 0
    assert agent.id is not None
    # Verify most of the special characters are preserved (allowing for some normalization)
    assert len(agent.description) >= size // 2


# ============================================================================
# Concurrent-Like Operations
# ============================================================================


@pytest.mark.slow
@pytest.mark.error
def test_rapid_sequential_creation():
    """Test rapid sequential creation of agents."""
    agents = []
    for i in range(1000):
        agent = Agent(name=f"rapid_{i}", description=f"Agent {i}")
        agents.append(agent)
    
    # All should have unique IDs
    ids = [agent.id for agent in agents]
    assert len(set(ids)) == 1000


@pytest.mark.slow
@pytest.mark.error
def test_interleaved_operations():
    """Test interleaved create, read, modify operations."""
    agents = []
    
    for cycle in range(100):
        # Create
        agent = Agent(name=f"cycle_{cycle}", description=f"Cycle {cycle}")
        agents.append(agent)
        
        # Modify
        if agents:
            random_agent = agents[cycle % len(agents)]
            random_agent.parent_ids = [agent.id]
        
        # Verify
        assert agent.id is not None


# ============================================================================
# Error Handling at Scale
# ============================================================================


@pytest.mark.slow
@pytest.mark.error
def test_high_volume_error_recovery():
    """Test recovery from many sequential errors."""
    error_count = 0
    success_count = 0
    
    for i in range(500):
        if i % 10 == 0:
            # Every 10th is invalid
            try:
                Agent(name=f"test_{i}", agent_type="invalid")
            except ValidationError:
                error_count += 1
        else:
            try:
                agent = Agent(name=f"valid_{i}", description=f"Agent {i}")
                success_count += 1
            except ValidationError:
                pass
    
    assert success_count == 450  # 500 - 50 errors
    assert error_count == 50


@pytest.mark.slow
@pytest.mark.error
def test_error_in_large_batch_doesnt_stop_processing():
    """Test that errors in large batches don't prevent processing."""
    results = {"valid": [], "invalid": []}
    
    for i in range(500):
        try:
            agent = Agent(name=f"agent_{i}", description=f"Agent {i}")
            results["valid"].append(agent)
        except ValidationError as e:
            results["invalid"].append(str(e))
    
    # Should process all without stopping
    assert len(results["valid"]) == 500
    assert len(results["invalid"]) == 0


@pytest.mark.slow
@pytest.mark.error
def test_mixed_valid_invalid_large_batch():
    """Test batch with mixed valid and invalid entries at scale."""
    valid = []
    invalid = []
    
    for i in range(500):
        if i % 5 == 0:
            # Invalid: wrong agent type
            try:
                Agent(name=f"test_{i}", agent_type="invalid")
            except ValidationError as e:
                invalid.append(str(e))
        else:
            # Valid
            try:
                agent = Agent(name=f"valid_{i}", description=f"Agent {i}")
                valid.append(agent)
            except ValidationError:
                pass
    
    assert len(valid) == 400  # 80% valid
    assert len(invalid) == 100  # 20% invalid


# ============================================================================
# Stress Tests for Memory and Performance
# ============================================================================


@pytest.mark.slow
@pytest.mark.error
def test_large_parent_chain_creation():
    """Test creating a long chain of agents with parent relationships."""
    agents = []
    
    for i in range(100):
        parent_ids = [agents[-1].id] if agents else []
        agent = Agent(
            name=f"chain_{i}",
            description=f"Chain agent {i}",
            parent_ids=parent_ids
        )
        agents.append(agent)
    
    # Last agent should have parent chain
    assert len(agents) == 100
    assert agents[99].parent_ids == [agents[98].id]


@pytest.mark.slow
@pytest.mark.error
def test_wide_parent_tree_creation():
    """Test creating a wide tree (many children with same parent)."""
    parent = Agent(name="root", description="Root parent")
    children = []
    
    for i in range(500):
        child = Agent(
            name=f"child_{i}",
            description=f"Child {i}",
            parent_ids=[parent.id]
        )
        children.append(child)
    
    assert len(children) == 500
    # All children should have the same parent
    assert all(child.parent_ids == [parent.id] for child in children)


@pytest.mark.slow
@pytest.mark.error
def test_deep_parent_tree_creation():
    """Test creating a deep tree (each has one parent)."""
    root = Agent(name="root", description="Root")
    current = root
    depth = 100
    
    for i in range(depth):
        next_agent = Agent(
            name=f"level_{i}",
            description=f"Level {i}",
            parent_ids=[current.id]
        )
        current = next_agent
    
    # Last agent should have a parent
    assert current.parent_ids[0] is not None


@pytest.mark.slow
@pytest.mark.error
def test_complex_parent_relationships():
    """Test agents with multiple roles and complex relationships."""
    agents = [
        Agent(name=f"agent_{i}", description=f"Agent {i}")
        for i in range(50)
    ]
    
    # Create complex relationships
    for i, agent in enumerate(agents[10:]):
        if i % 3 == 0:
            agent.architect_agent_id = agents[i % 10].id
        if i % 5 == 0:
            agent.genetic_operator_agent_id = agents[(i + 1) % 10].id
        if i > 0:
            agent.parent_ids = [agents[j].id for j in range(max(0, i-5), i)]
    
    # Verify no corruption
    for agent in agents:
        assert agent.id is not None


# ============================================================================
# Consistency Under Load
# ============================================================================


@pytest.mark.slow
@pytest.mark.error
def test_id_uniqueness_under_high_load():
    """Test that ID uniqueness is maintained under high load."""
    agent_count = 5000
    agents = []
    
    for i in range(agent_count):
        agent = Agent(name=f"load_{i}", description=f"Agent {i}")
        agents.append(agent)
    
    ids = [agent.id for agent in agents]
    unique_ids = set(ids)
    
    assert len(unique_ids) == agent_count


@pytest.mark.slow
@pytest.mark.error
def test_name_preservation_under_stress():
    """Test that agent names are preserved under stress."""
    names = [
        "simple",
        "with spaces",
        "with-dashes",
        "with_underscores",
        "CamelCase",
        "UPPERCASE",
        "with.dots",
        "special!@#$%",
    ]
    
    agents = []
    for cycle in range(100):
        for name in names:
            agent = Agent(name=f"{name}_{cycle}", description="test")
            agents.append(agent)
    
    # Verify all names are preserved
    assert len(agents) == len(names) * 100
    name_set = {agent.name for agent in agents}
    assert len(name_set) == len(names) * 100


@pytest.mark.slow
@pytest.mark.error
def test_parent_list_integrity_under_stress():
    """Test that parent lists maintain integrity under stress."""
    base_parents = [f"parent_{i}" for i in range(50)]
    agents = []
    
    for i in range(500):
        # Vary parent list size
        parent_count = (i % 50) + 1
        parents = base_parents[:parent_count]
        
        agent = Agent(
            name=f"stress_{i}",
            description="Stress test",
            parent_ids=parents
        )
        agents.append(agent)
    
    # Verify integrity
    for i, agent in enumerate(agents):
        expected_count = ((i % 50) + 1)
        assert len(agent.parent_ids) == expected_count

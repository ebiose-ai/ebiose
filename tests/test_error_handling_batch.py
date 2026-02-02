"""Batch operation and error recovery tests.

This module tests error handling during batch operations, error recovery patterns,
and state consistency across complex scenarios.
"""

import pytest
from pydantic_core import ValidationError
from ebiose.core.agent import Agent


# ============================================================================
# Batch Operation Error Handling
# ============================================================================


@pytest.mark.error
def test_batch_creation_all_valid(batch_operations_data):
    """Test creating a batch of valid agents."""
    agents = []
    for config in batch_operations_data["valid_agents"]:
        agent = Agent(**config)
        agents.append(agent)
    
    assert len(agents) == len(batch_operations_data["valid_agents"])
    assert all(agent.id is not None for agent in agents)


@pytest.mark.error
def test_batch_creation_mixed_valid_invalid(batch_operations_data):
    """Test batch creation with mixed valid/invalid agents."""
    valid_count = 0
    error_count = 0
    
    for config in batch_operations_data["mixed_valid_invalid"]:
        try:
            Agent(**config)
            valid_count += 1
        except ValidationError:
            error_count += 1
    
    # Should have 3 valid and 2 invalid
    assert valid_count == 3
    assert error_count == 2


@pytest.mark.error
def test_batch_creation_all_invalid(batch_operations_data):
    """Test batch creation with all invalid agents."""
    error_count = 0
    
    for config in batch_operations_data["all_invalid"]:
        try:
            Agent(**config)
            assert False, "Should have raised ValidationError"
        except ValidationError:
            error_count += 1
    
    assert error_count == len(batch_operations_data["all_invalid"])


@pytest.mark.error
def test_batch_creation_partial_failure_recovery(batch_operations_data):
    """Test that partial batch failures don't prevent recovery."""
    agents = []
    errors = []
    
    for config in batch_operations_data["mixed_valid_invalid"]:
        try:
            agent = Agent(**config)
            agents.append(agent)
        except ValidationError as e:
            errors.append(str(e))
    
    # Should have some successes despite failures
    assert len(agents) > 0
    assert len(errors) > 0
    # Agents should be valid
    assert all(agent.id is not None for agent in agents)


@pytest.mark.error
def test_batch_operation_idempotence():
    """Test that repeating batch operations produces consistent results."""
    configs = [
        {"name": f"agent_{i}", "description": f"Agent {i}"}
        for i in range(10)
    ]
    
    # First batch
    batch1 = [Agent(**config) for config in configs]
    ids1 = {agent.name: agent.id for agent in batch1}
    
    # Second batch with same configs
    batch2 = [Agent(**config) for config in configs]
    ids2 = {agent.name: agent.id for agent in batch2}
    
    # Names should be the same, but IDs should be different
    assert ids1.keys() == ids2.keys()
    for name in ids1.keys():
        assert ids1[name] != ids2[name]


# ============================================================================
# Error Recovery and Resilience
# ============================================================================


@pytest.mark.error
def test_error_recovery_basic(error_recovery_scenarios):
    """Test basic error recovery pattern."""
    scenario = error_recovery_scenarios["invalid_then_valid"]
    
    # Invalid creation fails
    with pytest.raises(ValidationError):
        Agent(**scenario["invalid_kwargs"])
    
    # Recovery with valid creation succeeds
    agent = Agent(**scenario["valid_kwargs"])
    assert agent is not None
    assert agent.name == scenario["valid_kwargs"]["name"]


@pytest.mark.error
def test_error_recovery_multiple_attempts(error_recovery_scenarios):
    """Test recovery through multiple failed attempts."""
    scenario = error_recovery_scenarios["multiple_errors"]
    
    attempts = scenario["attempts"]
    pass_attempt = scenario["expected_pass_on_attempt"]
    
    for i, kwargs in enumerate(attempts):
        try:
            agent = Agent(**kwargs)
            if i == pass_attempt:
                # Should succeed on this attempt
                assert agent.id is not None
            else:
                # Earlier attempts should fail
                assert False, f"Attempt {i} should have failed"
        except ValidationError:
            if i < pass_attempt:
                # Expected to fail
                pass
            else:
                # Should have succeeded
                raise


@pytest.mark.error
def test_error_recovery_boundary_then_normal(error_recovery_scenarios):
    """Test recovery after boundary condition."""
    scenario = error_recovery_scenarios["boundary_then_normal"]
    
    # Edge case should work
    edge_agent = Agent(**scenario["edge_case"])
    assert edge_agent.id is not None
    assert len(edge_agent.name) == 10000
    
    # Normal case should work
    normal_agent = Agent(**scenario["normal_case"])
    assert normal_agent.id is not None
    assert normal_agent.name == "normal"


@pytest.mark.error
def test_cascade_failure_recovery():
    """Test recovery from cascade of failures."""
    failures = [
        {"name": "test", "agent_type": "invalid1"},
        {"name": "test", "agent_type": "invalid2"},
        {"name": "test", "agent_type": "invalid3"},
    ]
    
    success_count = 0
    for fail_config in failures:
        try:
            Agent(**fail_config)
        except ValidationError:
            success_count += 1
    
    # After failures, valid creation should work
    valid_agent = Agent(name="recovery", description="After cascade")
    assert valid_agent.id is not None
    assert success_count == len(failures)


# ============================================================================
# State Consistency and Transitions
# ============================================================================


@pytest.mark.error
def test_state_consistency_after_failed_creation(error_context_data):
    """Test that failed creation doesn't affect subsequent creation."""
    error_config = error_context_data["error_triggers"]["validation"]
    valid_config = error_context_data["agent_creation_contexts"]["minimal"]
    
    # Create a valid agent
    agent1 = Agent(**valid_config)
    agent1_id = agent1.id
    
    # Attempt invalid creation
    with pytest.raises(ValidationError):
        Agent(**error_config)
    
    # Create another valid agent - should work independently
    agent2 = Agent(**valid_config)
    agent2_id = agent2.id
    
    # IDs should be different
    assert agent1_id != agent2_id
    assert agent1.name == agent2.name
    assert agent1.description == agent2.description


@pytest.mark.error
def test_state_transitions_valid_sequence(state_transition_scenarios):
    """Test valid state transitions."""
    scenario = state_transition_scenarios["creation_to_modification"]
    
    # Create agent
    agent = Agent(**scenario["initial"])
    original_id = agent.id
    
    # Apply modifications
    for modification in scenario["modifications"]:
        for key, value in modification.items():
            setattr(agent, key, value)
    
    # ID should remain the same
    assert agent.id == original_id
    # Modifications should be applied
    assert agent.architect_agent_id == "arch-1"
    assert agent.genetic_operator_agent_id == "op-1"
    assert agent.parent_ids == ["p1", "p2"]


@pytest.mark.error
def test_role_transition_sequence(state_transition_scenarios):
    """Test agent type role transitions."""
    scenario = state_transition_scenarios["role_transitions"]
    agent = Agent(**scenario["base"])
    
    for transition in scenario["transitions"]:
        agent.agent_type = transition["agent_type"]
        # Agent should remain valid after transition
        assert agent.id is not None


@pytest.mark.error
def test_parent_list_operation_sequence(state_transition_scenarios):
    """Test parent list modifications across states."""
    scenario = state_transition_scenarios["parent_list_operations"]
    agent = Agent(name="test", description="test")
    
    for parent_list in [
        scenario["empty"],
        scenario["single"],
        scenario["multiple"],
        scenario["large"],
    ]:
        agent.parent_ids = parent_list
        assert len(agent.parent_ids) == len(parent_list)
        assert agent.parent_ids == parent_list


# ============================================================================
# Error Message Consistency
# ============================================================================


@pytest.mark.error
def test_error_message_consistency(error_message_expectations):
    """Test that error messages are consistent."""
    import re
    
    # Test missing name error
    with pytest.raises(ValidationError) as exc_info:
        Agent(description="test")
    
    error_msg = str(exc_info.value).lower()
    pattern = error_message_expectations["missing_name"]["pattern"]
    assert re.search(pattern, error_msg, re.IGNORECASE)


@pytest.mark.error
def test_error_message_invalid_type(error_message_expectations):
    """Test error message for invalid agent type."""
    import re
    
    with pytest.raises(ValidationError) as exc_info:
        Agent(name="test", agent_type="invalid")
    
    error_msg = str(exc_info.value)
    pattern = error_message_expectations["invalid_type"]["pattern"]
    assert re.search(pattern, error_msg)


# ============================================================================
# Context-Based Error Testing
# ============================================================================


@pytest.mark.error
def test_error_context_minimal_creation(error_context_data):
    """Test error handling with minimal context."""
    agent = Agent(**error_context_data["agent_creation_contexts"]["minimal"])
    assert agent.name == "test"
    assert agent.id is not None


@pytest.mark.error
def test_error_context_complete_creation(error_context_data):
    """Test error handling with complete context."""
    agent = Agent(**error_context_data["agent_creation_contexts"]["complete"])
    assert agent.name == "test"
    assert agent.architect_agent_id == "arch-1"
    assert agent.genetic_operator_agent_id == "op-1"


@pytest.mark.error
def test_error_trigger_validation(error_context_data):
    """Test that documented error triggers actually cause errors."""
    error_triggers = error_context_data["error_triggers"]
    
    # Validation error
    with pytest.raises(ValidationError):
        Agent(**error_triggers["validation"])
    
    # Missing required
    with pytest.raises(ValidationError):
        Agent(**error_triggers["missing_required"])
    
    # Type mismatch
    with pytest.raises((ValidationError, TypeError)):
        Agent(**error_triggers["type_mismatch"])


# ============================================================================
# Assertion Helper Usage
# ============================================================================


@pytest.mark.error
def test_assertion_helpers(assertion_helpers):
    """Test that assertion helpers work correctly."""
    agent = Agent(name="test", description="test")
    
    # Test valid_agent helper
    assert assertion_helpers["valid_agent"](agent)
    
    # Test properties helper
    assert assertion_helpers["properties"](
        agent,
        name="test",
        agent_type=None
    )


@pytest.mark.error
def test_assertion_error_messages(assertion_helpers):
    """Test error message assertion helper."""
    error_msg = "name: Field required"
    
    assert assertion_helpers["error_message"](
        error_msg,
        "name",
        "field"
    )


# ============================================================================
# Combined Error Scenarios
# ============================================================================


@pytest.mark.error
def test_combined_batch_and_recovery(batch_operations_data, error_recovery_scenarios):
    """Test batch operations combined with error recovery."""
    # Batch with mixed results
    batch = batch_operations_data["mixed_valid_invalid"]
    valid_agents = []
    error_count = 0
    
    for config in batch:
        try:
            agent = Agent(**config)
            valid_agents.append(agent)
        except ValidationError:
            error_count += 1
    
    # Test recovery
    recovery_config = error_recovery_scenarios["invalid_then_valid"]["valid_kwargs"]
    recovery_agent = Agent(**recovery_config)
    
    assert len(valid_agents) > 0
    assert error_count > 0
    assert recovery_agent.id is not None


@pytest.mark.error
def test_state_transition_with_error_recovery():
    """Test state transitions while handling errors."""
    # Create agent
    agent = Agent(name="test", description="test")
    original_id = agent.id
    
    # Try invalid transition
    try:
        agent.agent_type = "invalid"
        # If it succeeded, check it's actually invalid
        assert agent.agent_type == "invalid"
    except (ValidationError, ValueError):
        # Expected for strict validation
        pass
    
    # Agent should still be valid
    assert agent.id == original_id
    
    # Valid transition should work
    agent.agent_type = "architect"
    assert agent.agent_type == "architect"


@pytest.mark.error
def test_large_batch_with_error_handling(performance_stress_data):
    """Test error handling with large batches."""
    batch_size = performance_stress_data["bulk_agent_creation"]["large_batch"]
    
    agents = []
    for i in range(batch_size):
        try:
            agent = Agent(name=f"agent_{i}", description=f"Agent {i}")
            agents.append(agent)
        except ValidationError:
            pass
    
    # Should successfully create all agents
    assert len(agents) == batch_size
    
    # All IDs should be unique
    ids = [agent.id for agent in agents]
    assert len(set(ids)) == len(ids)

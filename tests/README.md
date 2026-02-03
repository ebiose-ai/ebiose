# Test Suite

## Quick Start

```bash
# Run all tests
pytest

# Run only unit tests (fast - ~0.2s)
pytest -m unit

# Run integration tests
pytest -m integration

# Skip slow tests
pytest -m "not slow"

# Generate coverage report
pytest --cov=ebiose --cov-report=html
open htmlcov/index.html
```

## Organization

**252 tests** across 8 files • **21 fixtures** • **~0.4s** execution

### Test Categories
- `@pytest.mark.unit` - Fast unit tests (45 tests, ~0.2s)
- `@pytest.mark.integration` - Multi-agent workflows (13 tests)
- `@pytest.mark.error` - Error handling (112 tests)
- `@pytest.mark.slow` - Stress/performance (21 tests)

### Test Files
| File | Tests | Purpose |
|------|-------|---------|
| `test_agent_creation.py` | 30 | Agent creation & initialization |
| `test_error_handling.py` | 41 | Basic error handling |
| `test_error_handling_advanced.py` | 27 | Advanced error scenarios |
| `test_error_handling_batch.py` | 23 | Batch operations |
| `test_error_handling_stress.py` | 32 | Stress & performance |
| `test_integration_agents.py` | 10 | Multi-agent workflows |
| `test_llm_api_initialization.py` | 5 | LLM API config |
| `test_llm_api_simple.py` | 3 | LLM API basics |

## Fixtures

All fixtures are defined in `conftest.py`:

### Agent Fixtures
- `basic_agent` - Minimal agent
- `architect_agent` - Agent with architect type
- `genetic_operator_agent` - Agent with operator type
- `agent_with_relations` - Complex agent with relationships
- `multiple_agents` - Collection of agents (parametrizable)

### Test Data Fixtures
- `error_cases` - Error test scenarios
- `edge_case_agents` - Boundary conditions
- `batch_operations_data` - Batch test configs
- `performance_stress_data` - Large-scale test data

### Helper Fixtures
- `assertion_helpers` - Common assertion functions
- `test_constants` - Boundary values (MAX_NAME_LENGTH, etc.)

See `conftest.py` docstring for complete dependency hierarchy.

## Common Commands

```bash
# Fast development loop
pytest -m unit -v

# Test specific file
pytest tests/test_agent_creation.py

# Combine markers
pytest -m "unit and not slow"

# Show coverage gaps
pytest --cov=ebiose --cov-report=term-missing

# Parallel execution (if pytest-xdist installed)
pytest -n auto
```

## CI/CD Integration

```yaml
# Example GitHub Actions
- name: Fast tests
  run: pytest -m unit

- name: Full suite with coverage
  run: pytest --cov=ebiose --cov-report=xml

- name: Upload coverage
  uses: codecov/codecov-action@v3
```

## Writing New Tests

### Guidelines
1. Add appropriate markers (`@pytest.mark.unit`, etc.)
2. Use existing fixtures from `conftest.py`
3. Add descriptive parametrize IDs: `ids=lambda x: f"count_{x}"`
4. Organize by test category
5. Run locally before committing

### Example
```python
@pytest.mark.unit
@pytest.mark.parametrize("count", [0, 1, 10, 100], ids=lambda x: f"agents_{x}")
def test_agent_creation_batch(count):
    """Test creating multiple agents."""
    agents = [Agent(name=f"agent_{i}") for i in range(count)]
    assert len(agents) == count
```

## Improvements Applied

### Phase 1
✅ Applied 171 pytest markers for selective execution  
✅ Configured coverage tracking (70% minimum)  
✅ Documented fixture dependency hierarchy

### Phase 2
✅ Created assertion helper functions (`assert_agent_has_valid_id`, etc.)  
✅ Centralized test constants (MAX_NAME_LENGTH, UNICODE_SAMPLES, etc.)  
✅ Added parametrize IDs to 10+ tests  
✅ Removed duplicate markers  

## Coverage

**Minimum:** 70% (configured in `pytest.ini`)

```bash
# Generate and view report
pytest --cov=ebiose --cov-report=html
open htmlcov/index.html
```

## Troubleshooting

### Tests not found
```bash
# Verify test discovery
pytest --collect-only
```

### Import errors
```bash
# Ensure package is installed
pip install -e .
```

### Marker warnings
```bash
# Markers are registered in pytest.ini
pytest --markers
```

---

**Maintainer:** ebiose-ai team  
**Last Updated:** February 2026

"""
Tests to verify the LLMApi initialization logic without importing the full modules.

This test module uses source code inspection to verify that the LLMApi implementation
adheres to expected patterns, avoiding potential dependency issues while still
validating core initialization logic.
"""

import pytest
from pathlib import Path


@pytest.fixture
def source_files():
    """Fixture to read and cache LLMApi source files."""
    llm_api_path = Path(__file__).parent.parent / "ebiose" / "core" / "llm_api.py"
    langgraph_api_path = Path(__file__).parent.parent / "ebiose" / "backends" / "langgraph" / "llm_api.py"
    
    with open(llm_api_path, 'r', encoding='utf-8') as f:
        llm_api_content = f.read()
    
    with open(langgraph_api_path, 'r', encoding='utf-8') as f:
        langgraph_api_content = f.read()
    
    return {
        'llm_api': llm_api_content,
        'langgraph': langgraph_api_content,
        'llm_api_path': llm_api_path,
        'langgraph_api_path': langgraph_api_path
    }


@pytest.mark.unit
def test_no_hardcoded_urls(source_files):
    """Verify that hardcoded URLs are not present in LLMApi implementations."""
    old_hardcoded_url = "https://ebiose-litellm.livelysmoke-ef8b125f.francecentral.azurecontainerapps.io/"
    
    assert old_hardcoded_url not in source_files['llm_api'], \
        "Found hardcoded URL in llm_api.py"
    
    assert old_hardcoded_url not in source_files['langgraph'], \
        "Found hardcoded URL in langgraph/llm_api.py"


@pytest.mark.unit
def test_conditional_base_url_logic(source_files):
    """Verify that conditional logic for lite_llm_api_base is present."""
    expected_patterns = [
        "if lite_llm_api_base is not None:",
        "Use provided base URL",
        "elif mode == \"local\" and ModelEndpoints.use_lite_llm():",
        "Use local configuration",
        "cls.lite_llm_api_base = None"
    ]
    
    for pattern in expected_patterns:
        assert pattern in source_files['llm_api'], \
            f"Missing pattern in llm_api.py: {pattern}"
        
        assert pattern in source_files['langgraph'], \
            f"Missing pattern in langgraph/llm_api.py: {pattern}"


@pytest.mark.unit
def test_modelendpoints_import(source_files):
    """Verify that ModelEndpoints is properly imported in llm_api.py."""
    assert "from ebiose.core.model_endpoint import ModelEndpoints" in source_files['llm_api'], \
        "ModelEndpoints not imported in llm_api.py"

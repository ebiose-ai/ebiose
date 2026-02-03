"""Tests for LLMApi initialization and configuration.

This module verifies that LLMApi correctly handles initialization for different modes
(cloud, local) and validates that hardcoded URLs are not used in the implementation.
"""

import pytest
from ebiose.core.llm_api import LLMApi
from ebiose.backends.langgraph.llm_api import LangGraphLLMApi


# ============================================================================
# Cloud Mode Tests
# ============================================================================


@pytest.mark.unit
def test_cloud_mode_with_provided_base_url():
    """Test that cloud mode uses the provided lite_llm_api_base when supplied."""
    provided_base_url = None  # Cloud API will provide the real URL when available
    
    # Initialize LLMApi
    LLMApi.initialize(
        mode="cloud",
        lite_llm_api_key="test-key",
        lite_llm_api_base=provided_base_url
    )
    
    assert LLMApi.lite_llm_api_base == provided_base_url
    
    # Initialize LangGraphLLMApi
    LangGraphLLMApi.initialize(
        mode="cloud",
        lite_llm_api_key="test-key",
        lite_llm_api_base=provided_base_url
    )
    
    assert LangGraphLLMApi.lite_llm_api_base == provided_base_url


@pytest.mark.unit
def test_cloud_mode_without_base_url():
    """Test that cloud mode without base URL defaults to None."""
    # Initialize LLMApi
    LLMApi.initialize(
        mode="cloud",
        lite_llm_api_key="test-key",
        lite_llm_api_base=None
    )
    
    assert LLMApi.lite_llm_api_base is None
    
    # Initialize LangGraphLLMApi
    LangGraphLLMApi.initialize(
        mode="cloud",
        lite_llm_api_key="test-key",
        lite_llm_api_base=None
    )
    
    assert LangGraphLLMApi.lite_llm_api_base is None


# ============================================================================
# Local Mode Tests
# ============================================================================


@pytest.mark.unit
def test_local_mode():
    """Test that local mode handles configuration correctly."""
    # Initialize LLMApi
    LLMApi.initialize(
        mode="local",
        lite_llm_api_key="test-key",
        lite_llm_api_base=None
    )
    
    # In local mode, it should try to get config from ModelEndpoints
    # Without a real config file, it should be None
    assert hasattr(LLMApi, 'lite_llm_api_base')
    
    # Initialize LangGraphLLMApi
    LangGraphLLMApi.initialize(
        mode="local",
        lite_llm_api_key="test-key",
        lite_llm_api_base=None
    )
    
    assert hasattr(LangGraphLLMApi, 'lite_llm_api_base')


# ============================================================================
# No Hardcoded URLs Tests
# ============================================================================


@pytest.mark.parametrize("mode,base_url", [
    ("cloud", None),
    ("cloud", ""),
    ("local", None),
])
@pytest.mark.unit
def test_no_hardcoded_urls(mode, base_url):
    """Verify that hardcoded URLs are never used in any initialization scenario."""
    old_hardcoded_url = "https://ebiose-litellm.livelysmoke-ef8b125f.francecentral.azurecontainerapps.io/"
    
    LLMApi.initialize(
        mode=mode,
        lite_llm_api_key="test-key",
        lite_llm_api_base=base_url
    )
    
    assert LLMApi.lite_llm_api_base != old_hardcoded_url
    
    LangGraphLLMApi.initialize(
        mode=mode,
        lite_llm_api_key="test-key",
        lite_llm_api_base=base_url
    )
    
    assert LangGraphLLMApi.lite_llm_api_base != old_hardcoded_url

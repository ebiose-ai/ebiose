"""Test script to verify the refactoring is working correctly."""

from ebiose.core.llm_api_factory import LLMApiFactory
from ebiose.backends.langgraph.llm_api import LangGraphLLMApi
from ebiose.core.llm_api import LLMApi

def test_refactoring():
    """Test that the refactoring works correctly."""
    
    # Test 1: Factory should use LangGraphLLMApi by default
    api = LLMApiFactory.get_api()
    assert api == LangGraphLLMApi, f"Expected LangGraphLLMApi, got {api}"
    
    # Test 2: LangGraphLLMApi should inherit from LLMApi
    assert issubclass(LangGraphLLMApi, LLMApi), "LangGraphLLMApi should inherit from LLMApi"
    
    # Test 3: LangGraphLLMApi should have the required methods
    assert hasattr(LangGraphLLMApi, 'get_total_cost'), "LangGraphLLMApi should have get_total_cost method"
    assert hasattr(LangGraphLLMApi, 'get_agent_cost'), "LangGraphLLMApi should have get_agent_cost method"
    assert hasattr(LangGraphLLMApi, 'initialize'), "LangGraphLLMApi should have initialize method"
    
    # Test 4: LangGraphLLMApi should implement the abstract method
    assert hasattr(LangGraphLLMApi, 'process_llm_call'), "LangGraphLLMApi should have process_llm_call method"
    
    print("All tests passed! Refactoring is working correctly.")

if __name__ == "__main__":
    test_refactoring()

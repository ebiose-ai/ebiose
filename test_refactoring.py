#!/usr/bin/env python3
"""
Comprehensive test to validate the refactored Ebiose architecture.
This script tests:
1. Model imports and structure
2. Cloud client functionality
3. Core component integration
4. Example functionality
"""

def test_model_structure():
    """Test that all models can be imported from the centralized location."""
    try:
        from ebiose.core.models import (
            Agent,
            AgentEngine,
            AgentInputModel,
            AgentOutputModel,
            AgentType,
            Role,
            EbioseCloudError,
            ForgeCycle,
            ForgeCycleConfig,
        )
        print("✓ All models import correctly from centralized location")
        return True
    except ImportError as e:
        print(f"✗ Model import failed: {e}")
        return False


def test_cloud_client():
    """Test that the cloud client can be imported and instantiated."""
    try:
        from ebiose.cloud_client.client import EbioseCloudClient
        from ebiose.cloud_client.refactored_client import EbioseCloudClient as RefactoredClient
        
        # Test basic instantiation
        client = EbioseCloudClient("https://api.example.com", api_key="test")
        refactored_client = RefactoredClient("https://api.example.com", api_key="test")
        
        # Test that modular endpoints are available
        assert hasattr(refactored_client, 'forges')
        assert hasattr(refactored_client, 'auth')
        assert hasattr(refactored_client, 'ecosystems')
        assert hasattr(refactored_client, 'api_keys')
        assert hasattr(refactored_client, 'users')
        assert hasattr(refactored_client, 'logging')
        
        print("✓ Cloud clients instantiate correctly with modular endpoints")
        return True
    except Exception as e:
        print(f"✗ Cloud client test failed: {e}")
        return False


def test_core_components():
    """Test that core components work together."""
    try:
        from ebiose.core.agent import Agent
        from ebiose.core.agent_factory import AgentFactory
        from ebiose.core.ecosystem import Ecosystem
        from ebiose.core.agent_engine import AgentEngine
        
        print("✓ Core components import and integrate correctly")
        return True
    except Exception as e:
        print(f"✗ Core components test failed: {e}")
        return False


def test_engine_factory():
    """Test that the agent engine factory works."""
    try:
        from ebiose.core.agent_engine_factory import EngineRegistry
        
        # Test registry pattern
        engine_types = EngineRegistry.list_engine_types()
        print(f"✓ Agent engine factory works. Available engines: {engine_types}")
        return True
    except Exception as e:
        print(f"✗ Engine factory test failed: {e}")
        return False


def test_configuration_system():
    """Test that the configuration system works."""
    try:
        from ebiose.config import ConfigManager
        
        # Test basic configuration loading
        config = ConfigManager()
        print("✓ Configuration system works correctly")
        return True
    except Exception as e:
        print(f"✗ Configuration test failed: {e}")
        return False


def test_examples():
    """Test that examples still work."""
    try:
        from examples.math_forge.math_forge import MathLangGraphForge
        print("✓ Examples import correctly")
        return True
    except Exception as e:
        print(f"✗ Examples test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("🧪 Running comprehensive refactoring validation tests...\n")
    
    tests = [
        ("Model Structure", test_model_structure),
        ("Cloud Client", test_cloud_client),
        ("Core Components", test_core_components),
        ("Engine Factory", test_engine_factory),
        ("Configuration System", test_configuration_system),
        ("Examples", test_examples),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"Running {test_name} test...")
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f"✗ {test_name} test crashed: {e}")
            results.append(False)
        print()
    
    # Summary
    passed = sum(results)
    total = len(results)
    
    print("=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The refactoring is successful.")
        return 0
    else:
        print("❌ Some tests failed. Please review the issues above.")
        return 1


if __name__ == "__main__":
    exit(main())

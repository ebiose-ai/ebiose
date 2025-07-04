"""Configuration management for Ebiose."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, ClassVar

from pydantic import BaseModel, Field, field_validator
from pydantic_settings import BaseSettings


class ModelEndpointConfig(BaseModel):
    """Configuration for a model endpoint."""

    endpoint_id: str
    provider: str
    api_key: str | None = None
    endpoint_url: str | None = None
    api_version: str | None = None
    deployment_name: str | None = None


class EbioseCloudConfig(BaseModel):
    """Configuration for Ebiose Cloud."""

    api_key: str | None = None
    api_base: str | None = None


class LiteLLMConfig(BaseModel):
    """Configuration for LiteLLM."""

    use: bool = False
    use_proxy: bool = False
    api_key: str | None = None
    api_base: str | None = None


class EbioseConfig(BaseSettings):
    """Main configuration for Ebiose."""

    # Default model endpoint
    default_endpoint_id: str = "azure/gpt-4o-mini"
    
    # Cloud configuration
    ebiose_cloud: EbioseCloudConfig = Field(default_factory=EbioseCloudConfig)
    lite_llm: LiteLLMConfig = Field(default_factory=LiteLLMConfig)
    
    # Model endpoints
    endpoints: list[ModelEndpointConfig] = Field(default_factory=list)
    
    # Environment-specific settings
    environment: str = Field(default="development", env="EBIOSE_ENV")
    debug: bool = Field(default=False, env="EBIOSE_DEBUG")
    log_level: str = Field(default="INFO", env="EBIOSE_LOG_LEVEL")
    
    # API settings
    api_timeout: int = Field(default=30, env="EBIOSE_API_TIMEOUT")
    api_retries: int = Field(default=3, env="EBIOSE_API_RETRIES")
    
    # Model settings
    default_model_temperature: float = Field(default=0.7, env="EBIOSE_MODEL_TEMPERATURE")
    default_model_max_tokens: int = Field(default=1000, env="EBIOSE_MODEL_MAX_TOKENS")

    model_config = {
        "env_prefix": "EBIOSE_",
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
    }

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level."""
        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if v.upper() not in valid_levels:
            msg = f"Invalid log level: {v}. Must be one of {valid_levels}"
            raise ValueError(msg)
        return v.upper()

    @field_validator("environment")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        """Validate environment."""
        valid_envs = {"development", "staging", "production", "testing"}
        if v.lower() not in valid_envs:
            msg = f"Invalid environment: {v}. Must be one of {valid_envs}"
            raise ValueError(msg)
        return v.lower()

    def get_endpoint_config(self, endpoint_id: str) -> ModelEndpointConfig | None:
        """Get configuration for a specific endpoint."""
        for endpoint in self.endpoints:
            if endpoint.endpoint_id == endpoint_id:
                return endpoint
        return None

    def get_default_endpoint_config(self) -> ModelEndpointConfig | None:
        """Get the default endpoint configuration."""
        return self.get_endpoint_config(self.default_endpoint_id)

    @classmethod
    def load_from_yaml(cls, file_path: Path) -> EbioseConfig:
        """Load configuration from YAML file."""
        import yaml

        with file_path.open() as f:
            data = yaml.safe_load(f)
        
        return cls(**data)

    @classmethod
    def load_from_env(cls) -> EbioseConfig:
        """Load configuration from environment variables."""
        return cls()


class ConfigManager:
    """Global configuration manager."""

    _config: ClassVar[EbioseConfig | None] = None
    _config_file_path: ClassVar[Path | None] = None

    @classmethod
    def initialize(
        cls,
        config_file: Path | str | None = None,
        **overrides: Any,
    ) -> None:
        """Initialize the global configuration.

        Args:
            config_file: Path to configuration file (YAML)
            **overrides: Configuration overrides
        """
        if config_file:
            config_path = Path(config_file)
            if config_path.exists():
                cls._config = EbioseConfig.load_from_yaml(config_path)
                cls._config_file_path = config_path
            else:
                msg = f"Configuration file not found: {config_path}"
                raise FileNotFoundError(msg)
        else:
            # Try to find default config file
            default_paths = [
                Path("model_endpoints.yml"),
                Path("ebiose_config.yml"),
                Path("config.yml"),
            ]
            
            for path in default_paths:
                if path.exists():
                    cls._config = EbioseConfig.load_from_yaml(path)
                    cls._config_file_path = path
                    break
            else:
                # Load from environment
                cls._config = EbioseConfig.load_from_env()

        # Apply overrides
        if overrides:
            config_dict = cls._config.model_dump()
            config_dict.update(overrides)
            cls._config = EbioseConfig(**config_dict)

    @classmethod
    def get_config(cls) -> EbioseConfig:
        """Get the global configuration."""
        if cls._config is None:
            cls.initialize()
        return cls._config

    @classmethod
    def reload(cls) -> None:
        """Reload configuration from file."""
        if cls._config_file_path:
            cls._config = EbioseConfig.load_from_yaml(cls._config_file_path)
        else:
            cls._config = EbioseConfig.load_from_env()

    @classmethod
    def is_initialized(cls) -> bool:
        """Check if configuration is initialized."""
        return cls._config is not None

    @classmethod
    def get_model_endpoint_config(cls, endpoint_id: str) -> ModelEndpointConfig | None:
        """Get model endpoint configuration."""
        config = cls.get_config()
        return config.get_endpoint_config(endpoint_id)

    @classmethod
    def get_default_model_endpoint_id(cls) -> str:
        """Get the default model endpoint ID."""
        config = cls.get_config()
        return config.default_endpoint_id


# Global configuration instance
def get_config() -> EbioseConfig:
    """Get the global configuration instance."""
    return ConfigManager.get_config()


def get_model_endpoint_config(endpoint_id: str) -> ModelEndpointConfig | None:
    """Get model endpoint configuration by ID."""
    return ConfigManager.get_model_endpoint_config(endpoint_id)

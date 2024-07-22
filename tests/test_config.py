import pytest
import os
from claude_vision.config import (
    get_config_path,
    load_config,
    save_config,
    CONFIG
)

@pytest.fixture
def temp_config_file(tmp_path):
    original_config_path = get_config_path()
    temp_config_path = tmp_path / "temp_config.yaml"
    
    def _temp_config_path():
        return str(temp_config_path)
    
    # Mock get_config_path to return our temporary path
    import claude_vision.config
    claude_vision.config.get_config_path = _temp_config_path
    
    yield temp_config_path
    
    # Restore original get_config_path
    claude_vision.config.get_config_path = lambda: original_config_path

def test_load_config(temp_config_file):
    # Save a test configuration
    test_config = {"TEST_KEY": "TEST_VALUE"}
    save_config(test_config)
    
    # Load the configuration
    loaded_config = load_config()
    
    assert loaded_config == test_config

def test_save_config(temp_config_file):
    test_config = {"SAVE_TEST_KEY": "SAVE_TEST_VALUE"}
    save_config(test_config)
    
    with open(temp_config_file, 'r') as f:
        content = f.read()
    
    assert "SAVE_TEST_KEY: SAVE_TEST_VALUE" in content

def test_config_defaults():
    assert "ANTHROPIC_API_KEY" in CONFIG
    assert "DEFAULT_PROMPT" in CONFIG
    assert "MAX_IMAGE_SIZE" in CONFIG
    assert "SUPPORTED_FORMATS" in CONFIG
    assert "DEFAULT_PERSONAS" in CONFIG
    assert "DEFAULT_STYLES" in CONFIG

def test_config_update():
    original_value = CONFIG.get("TEST_UPDATE_KEY", None)
    
    CONFIG["TEST_UPDATE_KEY"] = "TEST_UPDATE_VALUE"
    save_config(CONFIG)
    
    loaded_config = load_config()
    assert loaded_config["TEST_UPDATE_KEY"] == "TEST_UPDATE_VALUE"
    
    # Clean up
    if original_value is None:
        del CONFIG["TEST_UPDATE_KEY"]
    else:
        CONFIG["TEST_UPDATE_KEY"] = original_value
    save_config(CONFIG)
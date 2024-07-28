import os
import yaml
from typing import Dict, Any

CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".config", "claude_vision")
CONFIG_PATH = os.path.join(CONFIG_DIR, "config.yaml")

DEFAULT_CONFIG = {
    "ANTHROPIC_API_KEY": os.getenv("ANTHROPIC_API_KEY", ""),
    "DEFAULT_PROMPT": "Describe this image in detail.",
    "MAX_IMAGE_SIZE": [1568, 1568],  # Changed to list for YAML compatibility
    "SUPPORTED_FORMATS": ['JPEG', 'PNG', 'GIF', 'WEBP'],
    "DEFAULT_PERSONAS": {
        "art_critic": "You are an experienced art critic with a keen eye for detail and composition.",
        "botanist": "You are a knowledgeable botanist specializing in plant identification and ecology.",
        "fashion_designer": "You are a trendsetting fashion designer with an eye for style and innovation.",
    },
    "DEFAULT_STYLES": {
        "noir_detective": "Describe the scene as if you're a hard-boiled detective in a film noir.",
        "victorian_gent": "Me dear fellow, Analyze the image in the style of a Victorian-era gentleman scientist.",
        "sci_fi_author": "Describe the image as if it's a scene from a futuristic science fiction novel.",
    },
    "CONFIG_VERSION": 1  # Add a version number for future compatibility
}

CONFIG: Dict[str, Any] = {}

def load_config() -> None:
    global CONFIG
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, 'r') as f:
                loaded_config = yaml.safe_load(f)
            if loaded_config and isinstance(loaded_config, dict):
                CONFIG.update(loaded_config)
                # Convert MAX_IMAGE_SIZE back to tuple if it exists
                if 'MAX_IMAGE_SIZE' in CONFIG and isinstance(CONFIG['MAX_IMAGE_SIZE'], list):
                    CONFIG['MAX_IMAGE_SIZE'] = tuple(CONFIG['MAX_IMAGE_SIZE'])
        except yaml.YAMLError as e:
            print(f"Error loading config file: {e}")
            print("Falling back to default configuration.")
            CONFIG = DEFAULT_CONFIG.copy()
    else:
        CONFIG = DEFAULT_CONFIG.copy()
        save_config()  # Save default config if no file exists

def save_config() -> None:
    os.makedirs(CONFIG_DIR, exist_ok=True)
    config_to_save = CONFIG.copy()
    # Convert MAX_IMAGE_SIZE to list for YAML compatibility
    if 'MAX_IMAGE_SIZE' in config_to_save and isinstance(config_to_save['MAX_IMAGE_SIZE'], tuple):
        config_to_save['MAX_IMAGE_SIZE'] = list(config_to_save['MAX_IMAGE_SIZE'])
    with open(CONFIG_PATH, 'w') as f:
        yaml.dump(config_to_save, f, default_flow_style=False)

def update_config(key: str, value: Any) -> None:
    CONFIG[key] = value
    save_config()

def get_config(key: str, default: Any = None) -> Any:
    return CONFIG.get(key, default)

# Initialize configuration
load_config()

# Expose configuration variables
ANTHROPIC_API_KEY = CONFIG.get('ANTHROPIC_API_KEY', '')
DEFAULT_PROMPT = CONFIG.get('DEFAULT_PROMPT', '')
MAX_IMAGE_SIZE = CONFIG.get('MAX_IMAGE_SIZE', (1568, 1568))
SUPPORTED_FORMATS = CONFIG.get('SUPPORTED_FORMATS', [])
DEFAULT_PERSONAS = CONFIG.get('DEFAULT_PERSONAS', {})
DEFAULT_STYLES = CONFIG.get('DEFAULT_STYLES', {})
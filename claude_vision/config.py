import os
import yaml
from typing import Dict, List, Tuple

# Custom YAML loader to handle !!python/tuple
class CustomLoader(yaml.SafeLoader):
    pass

def construct_python_tuple(loader, node):
    return tuple(loader.construct_sequence(node))

CustomLoader.add_constructor('tag:yaml.org,2002:python/tuple', construct_python_tuple)

# Default values
ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
DEFAULT_PROMPT: str = "Describe this image in detail."
MAX_IMAGE_SIZE: Tuple[int, int] = (1568, 1568)
SUPPORTED_FORMATS: List[str] = ['JPEG', 'PNG', 'GIF', 'WEBP']

DEFAULT_PERSONAS: Dict[str, str] = {
    "art_critic": "You are an experienced art critic with a keen eye for detail and composition.",
    "botanist": "You are a knowledgeable botanist specializing in plant identification and ecology.",
    "fashion_designer": "You are a trendsetting fashion designer with an eye for style and innovation.",
}

DEFAULT_STYLES: Dict[str, str] = {
    "noir_detective": "Describe the scene as if you're a hard-boiled detective in a film noir.",
    "victorian_gent": "Me dear fellow, Analyze the image in the style of a Victorian-era gentleman scientist.",
    "sci_fi_author": "Describe the image as if it's a scene from a futuristic science fiction novel.",
}

def get_config_path() -> str:
    """Get the path to the config file."""
    home = os.path.expanduser("~")
    return os.path.join(home, ".config", "claude_vision", "config.yaml")

def load_config() -> Dict:
    """Load the config from file or return an empty dict if not found."""
    config_path = get_config_path()
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f:
                return yaml.load(f, Loader=CustomLoader)
        except yaml.YAMLError as e:
            print(f"Error loading config file: {e}")
    return {}

def save_config(config: Dict) -> None:
    """Save the config to file."""
    config_path = get_config_path()
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    with open(config_path, 'w') as f:
        yaml.dump(config, f, default_flow_style=False)

# Load the config
CONFIG: Dict = load_config()

# Update the config with default values if they're missing
default_values = {
    'ANTHROPIC_API_KEY': ANTHROPIC_API_KEY,
    'DEFAULT_PROMPT': DEFAULT_PROMPT,
    'MAX_IMAGE_SIZE': MAX_IMAGE_SIZE,
    'SUPPORTED_FORMATS': SUPPORTED_FORMATS,
    'DEFAULT_PERSONAS': DEFAULT_PERSONAS,
    'DEFAULT_STYLES': DEFAULT_STYLES,
}

for key, value in default_values.items():
    if key not in CONFIG:
        CONFIG[key] = value

# Save the updated config
save_config(CONFIG)

# Update global variables with loaded config
globals().update(CONFIG)
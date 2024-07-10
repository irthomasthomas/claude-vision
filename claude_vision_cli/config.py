import os
import yaml

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
DEFAULT_PROMPT = "Describe this image in detail."
MAX_IMAGE_SIZE = (1568, 1568)
SUPPORTED_FORMATS = ['JPEG', 'PNG', 'GIF', 'WEBP']

DEFAULT_PERSONAS = {
    "art_critic": "You are an experienced art critic with a keen eye for detail and composition.",
    "botanist": "You are a knowledgeable botanist specializing in plant identification and ecology.",
    "fashion_designer": "You are a trendsetting fashion designer with an eye for style and innovation.",
}

DEFAULT_STYLES = {
    "noir_detective": "Describe the scene as if you're a hard-boiled detective in a film noir.",
    "victorian_poet": "Analyze the image in the flowery, romantic style of a Victorian-era poet.",
    "sci_fi_author": "Describe the image as if it's a scene from a futuristic science fiction novel.",
}

def load_config(config_path='config.yaml'):
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    return {}

CONFIG = load_config()
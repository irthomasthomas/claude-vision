import os
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass, field
import yaml
from pathlib import Path

@dataclass
class Config:
    ANTHROPIC_API_KEY: str = field(default_factory=lambda: os.getenv("ANTHROPIC_API_KEY", ""))
    DEFAULT_PROMPT: str = "Describe this image in detail."
    MAX_IMAGE_SIZE: Tuple[int, int] = (1568, 1568)
    SUPPORTED_FORMATS: List[str] = field(default_factory=lambda: ['JPEG', 'PNG', 'GIF', 'WEBP'])
    DEFAULT_PERSONAS: Dict[str, str] = field(default_factory=lambda: {
        "art_critic": "You are an experienced art critic with a keen eye for detail and composition.",
        "botanist": "You are a knowledgeable botanist specializing in plant identification and ecology.",
        "fashion_designer": "You are a trendsetting fashion designer with an eye for style and innovation.",
    })
    DEFAULT_STYLES: Dict[str, str] = field(default_factory=lambda: {
        "noir_detective": "Describe the scene as if you're a hard-boiled detective in a film noir.",
        "victorian_gent": "Me dear fellow, Analyze the image in the style of a Victorian-era gentleman scientist.",
        "sci_fi_author": "Describe the image as if it's a scene from a futuristic science fiction novel.",
    })

class ConfigManager:
    def __init__(self):
        self.config = Config()
        self.config_path = self._get_config_path()

    @staticmethod
    def _get_config_path() -> Path:
        return Path.home() / ".config" / "claude_vision" / "config.yaml"

    def load_config(self) -> None:
        if self.config_path.exists():
            try:
                loaded_config = yaml.safe_load(self.config_path.read_text())
                if loaded_config:
                    self._update_config(loaded_config)
            except yaml.YAMLError as e:
                print(f"Error loading config file: {e}")
            except IOError as e:
                print(f"Error reading config file: {e}")

    def _update_config(self, loaded_config: Dict[str, Any]) -> None:
        for key, value in loaded_config.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)

    def save_config(self) -> None:
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            self.config_path.write_text(yaml.dump(self.config.__dict__, default_flow_style=False))
        except IOError as e:
            print(f"Error saving config file: {e}")

    def get_config(self) -> Config:
        return self.config

def initialize_config() -> Config:
    config_manager = ConfigManager()
    config_manager.load_config()
    config_manager.save_config()
    return config_manager.get_config()

# Initialize configuration
CONFIG = initialize_config()

# Update global variables with loaded config
globals().update(CONFIG.__dict__)
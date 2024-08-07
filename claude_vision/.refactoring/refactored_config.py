import os
import yaml
from typing import Dict, List, Tuple
from dataclasses import dataclass, field, asdict

@dataclass
class Configuration:
    ANTHROPIC_API_KEY: str = field(default_factory=lambda: os.getenv("ANTHROPIC_API_KEY", ""))
    DEFAULT_PROMPT: str = "Describe this image in detail."
    MAX_IMAGE_SIZE: Tuple[int, int] = (1568, 1568)
    SUPPORTED_FORMATS: List[str] = field(default_factory=lambda: ['JPEG', 'PNG', 'GIF', 'WEBP'])
    DEFAULT_PERSONAS: Dict[str, str] = field(default_factory=lambda: {
        "art_critic": "You are an experienced art critic with a keen eye for detail and composition.",
        "botanist": "You are a knowledgeable botanist specializing in plant identification and ecology.",
        "fashion_designer": "You are a trendsetting fashion designer with an eye for style and innovation.",
        "alt_text": "Generate detailed, context-aware alt-text for this image to improve web accessibility."
    })
    DEFAULT_STYLES: Dict[str, str] = field(default_factory=lambda: {
        "noir_detective": "Describe the scene as if you're a hard-boiled detective in a film noir.",
        "victorian_gent": "Me dear fellow, Analyze the image in the style of a Victorian-era gentleman scientist.",
        "sci_fi_author": "Describe the image as if it's a scene from a futuristic science fiction novel.",
    })

    @classmethod
    def get_config_path(cls) -> str:
        """Get the path to the config file."""
        home = os.path.expanduser("~")
        return os.path.join(home, ".config", "claude_vision", "config.yaml")

    @classmethod
    def load(cls) -> 'Configuration':
        """Load the config from file or return default configuration if not found."""
        config_path = cls.get_config_path()
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    config_dict = yaml.safe_load(f)
                    return cls(**config_dict)
            except yaml.YAMLError as e:
                print(f"Error loading config file: {e}")
        return cls()

    def save(self) -> None:
        """Save the config to file."""
        config_path = self.get_config_path()
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        with open(config_path, 'w') as f:
            yaml.dump(asdict(self), f, default_flow_style=False)

    def add_persona(self, name: str, description: str) -> None:
        """Add a new persona."""
        self.DEFAULT_PERSONAS[name] = description
        self.save()

    def edit_persona(self, name: str, new_description: str) -> None:
        """Edit an existing persona."""
        if name in self.DEFAULT_PERSONAS:
            self.DEFAULT_PERSONAS[name] = new_description
            self.save()
        else:
            raise ValueError(f"Persona '{name}' not found.")

    def delete_persona(self, name: str) -> None:
        """Delete a persona."""
        if name in self.DEFAULT_PERSONAS:
            del self.DEFAULT_PERSONAS[name]
            self.save()
        else:
            raise ValueError(f"Persona '{name}' not found.")

    def get_persona(self, name: str) -> str:
        """Get a persona description."""
        return self.DEFAULT_PERSONAS.get(name, "")

    def list_personas(self) -> Dict[str, str]:
        """List all personas."""
        return self.DEFAULT_PERSONAS.copy()

# Load the configuration
CONFIG = Configuration.load()
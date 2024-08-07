import click
import json
from typing import Dict, Any, List, Union
from enum import Enum
from dataclasses import dataclass
from jsonschema import validate, ValidationError

from .persona import PersonaManager
from .plugin_manager import PluginManager
from .config import Config
from .input_detector import detect_input_type
from .image_processing import process_image
from .video_processing import process_video

class InputType(Enum):
    IMAGE = "image"
    VIDEO = "video"

@dataclass
class AnalysisResult:
    result: Union[str, Dict[str, Any]]
    input_type: InputType
    persona: str

class ClaudeVisionCLI:
    def __init__(self):
        self.config = Config()
        self.persona_manager = PersonaManager(self.config)
        self.plugin_manager = PluginManager(self.config)

    @click.group()
    def cli(self):
        """Claude Vision CLI"""
        pass

    @cli.command()
    @click.argument('input_path', type=click.Path(exists=True))
    @click.option('--persona', help="Persona to use for analysis")
    @click.option('--output', type=click.Choice(['json', 'text']), default='text', help="Output format")
    def analyze(self, input_path: str, persona: str, output: str):
        """Analyze an image or video"""
        input_type = detect_input_type(input_path)
        persona_instance = self.persona_manager.get_persona(persona)

        if input_type == InputType.IMAGE:
            result = process_image(input_path, persona_instance)
        elif input_type == InputType.VIDEO:
            result = process_video(input_path, persona_instance)
        else:
            raise ValueError(f"Unsupported input type: {input_type}")

        analysis_result = AnalysisResult(result, input_type, persona)
        self._output_result(analysis_result, output)

    @cli.command()
    @click.argument('input_paths', nargs=-1, type=click.Path(exists=True))
    @click.option('--persona', help="Persona to use for comparison")
    @click.option('--criteria', help="Comparison criteria")
    @click.option('--output', type=click.Choice(['json', 'text']), default='text', help="Output format")
    def compare(self, input_paths: List[str], persona: str, criteria: str, output: str):
        """Compare multiple images or videos"""
        persona_instance = self.persona_manager.get_persona(persona)
        result = self._compare_inputs(input_paths, persona_instance, criteria)
        self._output_result(result, output)

    @cli.command()
    @click.argument('input_paths', nargs=-1, type=click.Path(exists=True))
    @click.option('--persona', help="Persona to use for timeline analysis")
    @click.option('--metrics', help="Analysis metrics")
    @click.option('--output', type=click.Choice(['json', 'text']), default='text', help="Output format")
    def timeline(self, input_paths: List[str], persona: str, metrics: str, output: str):
        """Perform timeline analysis on multiple images or videos"""
        persona_instance = self.persona_manager.get_persona(persona)
        result = self._analyze_timeline(input_paths, persona_instance, metrics)
        self._output_result(result, output)

    @cli.command()
    @click.option('--add-persona', type=click.Path(exists=True), help="Add a new persona from YAML file")
    @click.option('--install-plugin', type=click.Path(exists=True), help="Install a new plugin")
    @click.option('--list-personas', is_flag=True, help="List all available personas")
    @click.option('--list-plugins', is_flag=True, help="List all installed plugins")
    def config(self, add_persona: str, install_plugin: str, list_personas: bool, list_plugins: bool):
        """Manage Claude Vision configuration"""
        if add_persona:
            self.persona_manager.add_persona(add_persona)
            click.echo(f"Persona added: {add_persona}")
        elif install_plugin:
            self.plugin_manager.install_plugin(install_plugin)
            click.echo(f"Plugin installed: {install_plugin}")
        elif list_personas:
            personas = self.persona_manager.list_personas()
            for persona in personas:
                click.echo(persona)
        elif list_plugins:
            plugins = self.plugin_manager.list_plugins()
            for plugin in plugins:
                click.echo(plugin)

    def _compare_inputs(self, input_paths: List[str], persona: Any, criteria: str) -> AnalysisResult:
        # Implement comparison logic here
        pass

    def _analyze_timeline(self, input_paths: List[str], persona: Any, metrics: str) -> AnalysisResult:
        # Implement timeline analysis logic here
        pass

    def _output_result(self, result: AnalysisResult, output_format: str):
        if output_format == 'json':
            click.echo(json.dumps(result.__dict__, indent=2))
        else:
            click.echo(result.result)

def main():
    cli = ClaudeVisionCLI()
    cli.cli()

if __name__ == '__main__':
    main()
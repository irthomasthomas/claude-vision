import sys
import io
import json
from typing import List, Dict, Any, TypedDict, Optional, Union, Callable, AsyncGenerator
import click
import asyncio
from PIL import Image

from .video_utils import is_video_file
from .video_processing import analyze_video
from .json_utils import parse_json_input, format_json_output, parse_video_json_input, format_video_json_output
from .image_processing import process_multiple_images, convert_image_to_base64
from .claude_integration import claude_vision_analysis
from .advanced_features import visual_judge, image_evolution_analyzer, persona_based_analysis, comparative_time_series_analysis, generate_alt_text
from .config import CONFIG, save_config, set_config, get_config, list_config, reset_config
from .exceptions import ClaudeVisionError
from .analyze import analyze_content
from .compare import compare_images
from .interactive import interactive_session
from .persona import (
    add_persona, generate_persona, list_personas, edit_persona, delete_persona, show_persona
)
from .track import track_changes

OUTPUT_FORMATS = ["json", "md", "markdown", "text"]

class ContextObject(TypedDict):
    output: str
    stream: bool
    prompt: Optional[str]
    persona: Optional[str]
    interactive: bool

class PersonaData(TypedDict):
    name: str
    description: str
    template: Optional[str]

@click.group()
@click.option("--output", type=click.Choice(OUTPUT_FORMATS), default="text", help="Output format")
@click.option("--stream", is_flag=True, help="Stream the response in real-time")
@click.option("--prompt", help="Use a custom prompt or template")
@click.option("--persona", help="Apply a specific persona to the analysis")
@click.option("--interactive", is_flag=True, help="Enable interactive mode")
@click.pass_context
def cli(ctx: click.Context, output: str, stream: bool, prompt: Optional[str], persona: Optional[str], interactive: bool) -> None:
    """Main CLI group for the application."""
    ctx.ensure_object(dict)
    ctx.obj: ContextObject = {
        "output": output,
        "stream": stream,
        "prompt": prompt,
        "persona": persona,
        "interactive": interactive
    }

@cli.command()
@click.argument('input_file', type=click.Path(exists=True), required=False)
@click.option('--json-input', type=click.File('r'), help="JSON input for chained operations")
@click.option('--video', is_flag=True, help="Treat input as a video file")
@click.option('--frame-interval', type=int, default=30, help="Interval between frames to analyze in video")
@click.option('--num-workers', type=int, default=None, help="Number of worker processes for video analysis")
@click.option('--system', help="Custom system prompt for Claude")
@click.option('--prefill', help="Prefill Claude's response")
@click.option('--max-tokens', type=int, default=1000, help="Maximum number of tokens in the response")
@click.option('--group', is_flag=True, help="Process frames or images as a group")
@click.pass_context
async def analyze(ctx: click.Context, input_file: Optional[str], json_input: Optional[click.File], video: bool,
                  frame_interval: int, num_workers: Optional[int], system: Optional[str], prefill: Optional[str],
                  max_tokens: int, group: bool):
    """Analyze content based on input files."""
    try:
        if ctx.obj["interactive"]:
            await interactive_session(ctx)
        else:
            if not input_file and not sys.stdin.isatty():
                input_data = sys.stdin.buffer.read()
                input_file = io.BytesIO(input_data)
            await claude_vision_async(input_file, ctx.obj["persona"], json_input, ctx.obj["output"], ctx.obj["stream"],
                                      video, frame_interval, num_workers, ctx.obj["prompt"], system, prefill, max_tokens, group)
    except ClaudeVisionError as e:
        click.echo(f"Error: {str(e)}", err=True)
    except Exception as e:
        click.echo(f"An unexpected error occurred: {str(e)}", err=True)

async def claude_vision_async(input_file: Union[str, io.BytesIO], persona: Optional[str], json_input: Optional[click.File],
                              output: str, stream: bool, video: bool, frame_interval: int, num_workers: Optional[int],
                              prompt: Optional[str], system: Optional[str], prefill: Optional[str], max_tokens: int, group: bool):
    try:
        data = parse_input_data(json_input, video, input_file, persona, frame_interval)
        
        if video or (isinstance(input_file, str) and is_video_file(input_file)):
            await process_video(input_file, frame_interval, persona, output, stream, num_workers, prompt, system, group)
        else:
            await process_image(input_file, persona, output, stream, prompt, system, prefill, max_tokens, group)

    except ClaudeVisionError as e:
        click.echo(f"Error: {str(e)}", err=True)
    except Exception as e:
        click.echo(f"An unexpected error occurred: {str(e)}", err=True)

def parse_input_data(json_input, video, input_file, persona, frame_interval):
    if json_input:
        data = parse_video_json_input(json_input) if video else parse_json_input(json_input)
        return {
            'input_file': data['file_path'],
            'persona': data.get('persona', persona),
            'analysis_type': data['analysis_type'],
            'frame_interval': data.get('frame_interval', frame_interval)
        }
    elif not input_file:
        raise ClaudeVisionError("Please provide an input file, pipe input, or JSON input.")
    return {'input_file': input_file, 'persona': persona, 'frame_interval': frame_interval}

async def process_video(input_file, frame_interval, persona, output, stream, num_workers, prompt, system, group):
    metadata, frame_results = await analyze_video(input_file, frame_interval, persona, output, stream, num_workers, prompt=prompt, system=system, process_as_group=group)
    
    if output == 'json':
        formatted_result = format_video_json_output(metadata, frame_results, "video_description")
        click.echo(json.dumps(formatted_result, indent=2, ensure_ascii=False))
    else:
        for result in frame_results:
            click.echo(f"Frame {result['frame_number']} ({result['timestamp']:.2f}s): {result['result']}")

async def process_image(input_file, persona, output, stream, prompt, system, prefill, max_tokens, group):
    base64_images = await get_base64_images(input_file, group)
    prompt = prompt or generate_prompt(persona)

    result = await claude_vision_analysis(base64_images, prompt, output, stream, system=system, max_tokens=max_tokens, prefill=prefill)
    await output_result(result, output, stream)

async def get_base64_images(input_file, group):
    if isinstance(input_file, io.BytesIO):
        image = Image.open(input_file)
        return [convert_image_to_base64(image)]
    return await process_multiple_images([input_file], process_as_group=group)

async def output_result(result: Union[str, AsyncGenerator[str, None]], output: str, stream: bool):
    if output == 'json':
        await output_json(result, stream)
    elif output in ['md', 'markdown']:
        await output_markdown(result, stream)
    else:
        await output_text(result, stream)

async def output_json(result, stream):
    if stream:
        async for chunk in result:
            click.echo(chunk, nl=False)
        click.echo()
    else:
        formatted_result = format_json_output(result, "description")
        click.echo(json.dumps(formatted_result, indent=2, ensure_ascii=False))

async def output_markdown(result, stream):
    if stream:
        async for chunk in result:
            click.echo(chunk, nl=False)
        click.echo()
    else:
        click.echo(result)

async def output_text(result, stream):
    if stream:
        async for chunk in result:
            click.echo(chunk, nl=False)
        click.echo()
    else:
        click.echo(result)

@cli.command()
@click.argument("input_files", nargs=-1, type=click.Path(exists=True), required=True)
@click.option("--criteria", required=True, help="Comma-separated list of criteria")
@click.option("--weights", required=True, help="Comma-separated list of weights")
@click.pass_context
async def compare(ctx: click.Context, input_files: List[str], criteria: str, weights: str) -> None:
    """Compare images based on given criteria and weights."""
    try:
        await compare_images(
            input_files, 
            criteria.split(","), 
            [float(w) for w in weights.split(",")],
            **ctx.obj
        )
    except ClaudeVisionError as e:
        click.echo(f"Error: {str(e)}", err=True)
    except Exception as e:
        click.echo(f"An unexpected error occurred: {str(e)}", err=True)

@cli.command()
@click.argument("input_files", nargs=-1, type=click.Path(exists=True), required=True)
@click.option("--time-points", required=True, help="Comma-separated list of time points")
@click.option("--metrics", required=True, help="Comma-separated list of metrics to analyze")
@click.pass_context
async def track(ctx: click.Context, input_files: List[str], time_points: str, metrics: str) -> None:
    """Track changes in input files over time based on given metrics."""
    try:
        await track_changes(
            input_files, 
            time_points.split(","), 
            metrics.split(","),
            **ctx.obj
        )
    except ClaudeVisionError as e:
        click.echo(f"Error: {str(e)}", err=True)
    except Exception as e:
        click.echo(f"An unexpected error occurred: {str(e)}", err=True)

@cli.group()
def persona() -> None:
    """Group for persona-related commands."""
    pass

def persona_command(func: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator for persona commands to standardize output and error handling."""
    @persona.command(func.__name__.replace("_", "-"))
    @click.pass_context
    async def wrapper(ctx: click.Context, *args: Any, **kwargs: Any) -> None:
        try:
            result = await func(*args, **kwargs)
            click.echo(result)
        except ClaudeVisionError as e:
            click.echo(f"Error: {str(e)}", err=True)
        except Exception as e:
            click.echo(f"An unexpected error occurred: {str(e)}", err=True)
    return wrapper

@persona_command
async def add(name: str, description: str) -> str:
    """Add a new persona."""
    await add_persona(name, description)
    return f"Persona '{name}' added successfully."

@persona_command
async def generate(description: str) -> str:
    """Generate a new persona based on description."""
    await generate_persona(description)
    return "New persona generated successfully."

@persona_command
async def list() -> str:
    """List all personas."""
    personas = await list_personas()
    return "\n".join(personas)

@persona_command
async def edit(name: str) -> str:
    """Edit an existing persona."""
    await edit_persona(name)
    return f"Persona '{name}' updated successfully."

@persona_command
async def delete(name: str) -> str:
    """Delete a persona."""
    await delete_persona(name)
    return f"Persona '{name}' deleted successfully."

@persona_command
async def show(name: str) -> str:
    """Show details of a specific persona."""
    persona_data: PersonaData = await show_persona(name)
    return "\n".join([
        f"Name: {persona_data['name']}",
        f"Description: {persona_data['description']}",
        f"Template: {persona_data.get('template', 'N/A')}"
    ])

@cli.group()
def config() -> None:
    """Group for configuration-related commands."""
    pass

@config.command("set")
@click.argument("key")
@click.argument("value")
async def config_set(key: str, value: str) -> None:
    """Set a configuration value."""
    try:
        await set_config(key, value)
        click.echo(f"Configuration '{key}' set to '{value}'.")
    except ClaudeVisionError as e:
        click.echo(f"Error: {str(e)}", err=True)
    except Exception as e:
        click.echo(f"An unexpected error occurred: {str(e)}", err=True)

@config.command("get")
@click.argument("key")
async def config_get(key: str) -> None:
    """Get a configuration value."""
    try:
        value = await get_config(key)
        click.echo(f"{key}: {value}")
    except ClaudeVisionError as e:
        click.echo(f"Error: {str(e)}", err=True)
    except Exception as e:
        click.echo(f"An unexpected error occurred: {str(e)}", err=True)

@config.command("list")
async def config_list() -> None:
    """List all configuration settings."""
    try:
        configs = await list_config()
        for k, v in configs.items():
            click.echo(f"{k}: {v}")
    except ClaudeVisionError as e:
        click.echo(f"Error: {str(e)}", err=True)
    except Exception as e:
        click.echo(f"An unexpected error occurred: {str(e)}", err=True)

@config.command("reset")
async def config_reset() -> None:
    """Reset all configuration settings to default."""
    try:
        await reset_config()
        click.echo("Configuration reset to default.")
    except ClaudeVisionError as e:
        click.echo(f"Error: {str(e)}", err=True)
    except Exception as e:
        click.echo(f"An unexpected error occurred: {str(e)}", err=True)

if __name__ == "__main__":
    asyncio.run(cli())
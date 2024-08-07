import sys
import io
from PIL import Image
import json
from typing import List, Union, AsyncGenerator
import click
import asyncio
from .core import (
    process_multiple_images,
    convert_image_to_base64,
    claude_vision_analysis,
    is_video_file,
    analyze_video,
    parse_json_input,
    format_json_output,
    parse_video_json_input,
    format_video_json_output,
    Configuration,
    ClaudeVisionError
)
from .persona import (
    add_persona,
    edit_persona,
    list_personas,
    delete_persona
)
from .plugin_manager import PluginManager

config = Configuration()
plugin_manager = PluginManager(config)

@click.group()
def cli():
    """Claude Vision CLI"""
    pass

@cli.command()
@click.argument('input-file', type=click.Path(exists=True), required=False)
@click.option('--persona', help="Optional persona for analysis")
@click.option('--json-input', type=click.File('r'), help="JSON input for chained operations")
@click.option('--output', type=click.Choice(['json', 'md', 'markdown', 'text']), default='text', help="Output format")
@click.option('--stream', is_flag=True, help="Stream the response in real-time")
@click.option('--video', type=int, help="Treat input as a video file and set frame interval")
@click.option('--num-workers', type=int, default=None, help="Number of worker processes for video analysis")
@click.option('--prompt', help="Custom prompt for analysis")
@click.option('--system', help="Custom system prompt for Claude")
@click.option('--prefill', help="Prefill Claude's response")
@click.option('--max-tokens', type=int, default=1000, help="Maximum number of tokens in the response")
def analyze(input_file, persona, json_input, output, stream, video, num_workers, prompt, system, prefill, max_tokens):
    """Analyze an image or video"""
    if not input_file and not sys.stdin.isatty():
        input_data = sys.stdin.buffer.read()
        input_file = io.BytesIO(input_data)
    try:
        asyncio.run(claude_vision_async(input_file, persona, json_input, output, stream, video, num_workers, prompt, system, prefill, max_tokens))
    except ClaudeVisionError as e:
        click.echo(f"Error: {str(e)}", err=True)
    except Exception as e:
        click.echo(f"An unexpected error occurred: {str(e)}", err=True)

@cli.command()
@click.option('--add', help="Add a new persona")
@click.option('--edit', help="Edit an existing persona")
@click.option('--list', 'list_all', is_flag=True, help="List all available personas")
@click.option('--delete', help="Delete a persona")
def persona(add, edit, list_all, delete):
    """Manage personas"""
    try:
        if add:
            description = click.prompt("Enter persona description")
            add_persona(add, description)
            click.echo(f"Added persona: {add}")
        elif edit:
            description = click.prompt("Enter new persona description")
            edit_persona(edit, description)
            click.echo(f"Updated persona: {edit}")
        elif list_all:
            personas = list_personas()
            for name, description in personas.items():
                click.echo(f"{name}: {description}")
        elif delete:
            delete_persona(delete)
            click.echo(f"Deleted persona: {delete}")
        else:
            click.echo("Please specify an action: --add, --edit, --list, or --delete")
    except ClaudeVisionError as e:
        click.echo(f"Error: {str(e)}", err=True)

@cli.command()
@click.option('--key', help="Config key to set or get")
@click.option('--value', help="Value to set for the config key")
@click.option('--add-plugin', type=click.Path(exists=True), help="Add a new plugin")
@click.option('--list-plugins', is_flag=True, help="List all installed plugins")
def config(key, value, add_plugin, list_plugins):
    """Manage Claude Vision configuration and plugins"""
    if key and value:
        config.set(key, value)
        click.echo(f"Set {key} to {value}")
    elif key:
        click.echo(f"{key}: {config.get(key, 'Not set')}")
    elif add_plugin:
        plugin_manager.install_plugin(add_plugin)
        click.echo(f"Plugin installed: {add_plugin}")
    elif list_plugins:
        plugins = plugin_manager.list_plugins()
        for plugin in plugins:
            click.echo(plugin)
    else:
        for k, v in config.items():
            click.echo(f"{k}: {v}")

async def claude_vision_async(input_file, persona, json_input, output, stream, video, num_workers, prompt, system, prefill, max_tokens):
    if json_input:
        data = parse_video_json_input(json_input) if video else parse_json_input(json_input)
        input_file = data['file_path']
        persona = data.get('persona', persona)
        video = data.get('frame_interval', video)

    if not input_file:
        raise click.UsageError("Please provide an input file, pipe input, or JSON input.")

    if video or (isinstance(input_file, str) and is_video_file(input_file)):
        await process_video(input_file, video, persona, output, stream, num_workers, prompt, system)
    else:
        await process_image(input_file, persona, output, stream, prompt, system, prefill, max_tokens)

async def process_video(input_file, frame_interval, persona, output, stream, num_workers, prompt, system):
    metadata, frame_results = await analyze_video(input_file, frame_interval, persona, output, stream, num_workers, prompt=prompt, system=system)
    
    if output == 'json':
        formatted_result = format_video_json_output(metadata, frame_results, "video_description")
        click.echo(json.dumps(formatted_result, indent=2, ensure_ascii=False))
    else:
        for result in frame_results:
            click.echo(f"Frame {result['frame_number']} ({result['timestamp']:.2f}s): {result['result']}")

async def process_image(input_file, persona, output, stream, prompt, system, prefill, max_tokens):
    if isinstance(input_file, io.BytesIO):
        image = Image.open(input_file)
        base64_images = [convert_image_to_base64(image)]
    else:
        base64_images = await process_multiple_images([input_file])
    
    if not prompt:
        prompt = generate_prompt(persona)

    result = await claude_vision_analysis(
        base64_images, prompt, output, stream, 
        system=system, 
        max_tokens=max_tokens, 
        prefill=prefill
    )
    output_result(result, output, stream)

def generate_prompt(persona=None):
    base_prompt = "Analyze this image and provide a detailed description."
    if persona:
        return f"As a {persona}, {base_prompt}"
    return base_prompt

def output_result(result: Union[str, AsyncGenerator[str, None]], output: str, stream: bool):
    if output == 'json':
        if stream:
            asyncio.run(stream_output(result))
        else:
            formatted_result = format_json_output(result, "description")
            click.echo(json.dumps(formatted_result, indent=2, ensure_ascii=False))
    elif output in ['md', 'markdown']:
        if stream:
            asyncio.run(stream_output(result))
        else:
            click.echo(result)
    else:
        if stream:
            asyncio.run(stream_output(result))
        else:
            click.echo(result)

async def stream_output(result: AsyncGenerator[str, None]):
    async for chunk in result:
        click.echo(chunk, nl=False)
    click.echo()

if __name__ == '__main__':
    cli()
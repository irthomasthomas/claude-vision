import sys
import io
import json
from typing import List, Optional, Union, AsyncGenerator, Dict, Any
import click
import asyncio
from PIL import Image

from .video_utils import is_video_file
from .video_processing import analyze_video
from .json_utils import parse_json_input, format_json_output, parse_video_json_input, format_video_json_output
from .image_processing import process_multiple_images, convert_image_to_base64
from .claude_integration import claude_vision_analysis
from .advanced_features import ImageAnalyzer, AnalysisParams, OutputType
from .config import CONFIG, save_config
from .exceptions import ClaudeVisionError

@click.group()
def cli():
    """Claude Vision CLI tool."""
    pass

@cli.command()
@click.argument('input_file', type=click.Path(exists=True), required=False)
@click.option('--persona', help="Optional persona for analysis")
@click.option('--json-input', type=click.File('r'), help="JSON input for chained operations")
@click.option('--output', type=click.Choice(['json', 'md', 'markdown', 'text']), default='text', help="Output format")
@click.option('--stream', is_flag=True, help="Stream the response in real-time")
@click.option('--video', is_flag=True, help="Treat input as a video file")
@click.option('--frame-interval', type=int, default=30, help="Interval between frames to analyze in video")
@click.option('--num-workers', type=int, default=None, help="Number of worker processes for video analysis")
@click.option('--prompt', help="Custom prompt for analysis")
@click.option('--system', help="Custom system prompt for Claude")
@click.option('--prefill', help="Prefill Claude's response")
@click.option('--max-tokens', type=int, default=1000, help="Maximum number of tokens in the response")
@click.option('--group', is_flag=True, help="Process frames or images as a group")
def analyze(input_file: Optional[str], **kwargs):
    """Analyze input using Claude Vision."""
    if not input_file and not sys.stdin.isatty():
        input_data = sys.stdin.buffer.read()
        input_file = io.BytesIO(input_data)
    asyncio.run(claude_vision_async(input_file, **kwargs))


@cli.command()
@click.argument('image_paths', nargs=-1, type=click.Path(exists=True), required=True)
@click.option('--time-points', required=True, help="Comma-separated list of time points")
@click.option('--metrics', required=True, help="Comma-separated list of metrics to analyze")
@click.option('--output', type=click.Choice(['json', 'md', 'markdown', 'text']), default='text', help="Output format")
@click.option('--stream', is_flag=True, help="Stream the response in real-time")
@click.option('--prompt', help="Custom prompt for time-series analysis")
async def time_series(image_paths: List[str], time_points: str, metrics: str, output: str, stream: bool, prompt: Optional[str]):
    """Perform time-series analysis on multiple images."""
    try:
        base64_images = await process_multiple_images(image_paths)
        time_points_list = time_points.split(',')
        metrics_list = metrics.split(',')
        
        params = AnalysisParams(
            base64_images=base64_images,
            output_type=OutputType(output),
            stream=stream,
            user_prompt=prompt
        )
        
        result = await ImageAnalyzer.comparative_time_series_analysis(params, time_points_list, metrics_list)
        await output_result(result, output, stream)
    except Exception as e:
        click.echo(f"An error occurred during time-series analysis: {str(e)}", err=True)

@cli.command()
@click.argument('image_paths', nargs=-1, type=click.Path(exists=True), required=True)
@click.option('--time-points', required=True, help="Comma-separated list of time points")
@click.option('--output', type=click.Choice(['json', 'md', 'markdown', 'text']), default='text', help="Output format")
@click.option('--stream', is_flag=True, help="Stream the response in real-time")
@click.option('--prompt', help="Custom prompt for evolution analysis")
async def evolution(image_paths: List[str], time_points: str, output: str, stream: bool, prompt: Optional[str]):
    """Perform evolutionary analysis on multiple images."""
    try:
        base64_images = await process_multiple_images(image_paths)
        time_points_list = time_points.split(',')
        
        params = AnalysisParams(
            base64_images=base64_images,
            output_type=OutputType(output),
            stream=stream,
            user_prompt=prompt
        )
        
        result = await ImageAnalyzer.image_evolution_analyzer(params, time_points_list)
        await output_result(result, output, stream)
    except Exception as e:
        click.echo(f"An error occurred during evolution analysis: {str(e)}", err=True)
async def claude_vision_async(input_file: Union[str, io.BytesIO], **kwargs):
    """Asynchronous wrapper for Claude Vision analysis."""
    try:
        data = parse_input_data(kwargs.get('json_input'), kwargs.get('video'), input_file, kwargs.get('persona'), kwargs.get('frame_interval'))
        
        if kwargs.get('video') or (isinstance(input_file, str) and is_video_file(input_file)):
            await process_video(input_file, **kwargs)
        else:
            await process_image(input_file, **kwargs)

    except ClaudeVisionError as e:
        click.echo(f"Error: {str(e)}", err=True)
    except Exception as e:
        click.echo(f"An unexpected error occurred: {str(e)}", err=True)

def parse_input_data(json_input: Optional[click.File], video: bool, input_file: Union[str, io.BytesIO], persona: Optional[str], frame_interval: int) -> Dict[str, Any]:
    """Parse input data from various sources."""
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

async def process_video(input_file: Union[str, io.BytesIO], **kwargs):
    """Process video input."""
    metadata, frame_results = await analyze_video(
        input_file, 
        kwargs.get('frame_interval', 30), 
        kwargs.get('persona'),
        kwargs.get('output', 'text'),
        kwargs.get('stream', False),
        kwargs.get('num_workers'),
        prompt=kwargs.get('prompt'),
        system=kwargs.get('system'),
        process_as_group=kwargs.get('group', False)
    )
    
    if kwargs.get('output') == 'json':
        formatted_result = format_video_json_output(metadata, frame_results, "video_description")
        click.echo(json.dumps(formatted_result, indent=2, ensure_ascii=False))
    else:
        for result in frame_results:
            click.echo(f"Frame {result['frame_number']} ({result['timestamp']:.2f}s): {result['result']}")

async def process_image(input_file: Union[str, io.BytesIO], **kwargs):
    """Process image input."""
    base64_images = await get_base64_images(input_file, kwargs.get('group', False))
    prompt = kwargs.get('prompt') or generate_prompt(kwargs.get('persona'))

    result = await claude_vision_analysis(
        base64_images, 
        prompt, 
        kwargs.get('output', 'text'),
        kwargs.get('stream', False),
        system=kwargs.get('system'),
        max_tokens=kwargs.get('max_tokens', 1000),
        prefill=kwargs.get('prefill')
    )
    await output_result(result, kwargs.get('output', 'text'), kwargs.get('stream', False))

async def get_base64_images(input_file: Union[str, io.BytesIO], group: bool) -> List[str]:
    """Convert input to base64 images."""
    if isinstance(input_file, io.BytesIO):
        image = Image.open(input_file)
        return [convert_image_to_base64(image)]
    return await process_multiple_images([input_file], process_as_group=group)

async def output_result(result: Union[str, AsyncGenerator[str, None]], output: str, stream: bool):
    """Output the result based on the specified format."""
    output_funcs = {
        'json': output_json,
        'md': output_markdown,
        'markdown': output_markdown,
        'text': output_text
    }
    await output_funcs.get(output, output_text)(result, stream)

async def output_json(result: Union[str, AsyncGenerator[str, None]], stream: bool):
    """Output result in JSON format."""
    if stream:
        async for chunk in result:
            click.echo(chunk, nl=False)
        click.echo()
    else:
        formatted_result = format_json_output(result, "description")
        click.echo(json.dumps(formatted_result, indent=2, ensure_ascii=False))

async def output_markdown(result: Union[str, AsyncGenerator[str, None]], stream: bool):
    """Output result in Markdown format."""
    await output_stream_or_full(result, stream)

async def output_text(result: Union[str, AsyncGenerator[str, None]], stream: bool):
    """Output result as plain text."""
    await output_stream_or_full(result, stream)

async def output_stream_or_full(result: Union[str, AsyncGenerator[str, None]], stream: bool):
    """Helper function to handle both streaming and full output."""
    if stream:
        async for chunk in result:
            click.echo(chunk, nl=False)
        click.echo()
    else:
        click.echo(result)

def generate_prompt(persona: Optional[str]) -> str:
    """Generate a prompt based on the persona."""
    base_prompt = "Analyze the following image(s) and provide a detailed description."
    return f"As a {persona}, {base_prompt}" if persona else base_prompt

if __name__ == '__main__':
    cli()
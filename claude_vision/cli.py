import sys
import io
import json
from typing import List, Optional, Union, AsyncGenerator
import click
import asyncio
from PIL import Image

from .video_utils import is_video_file
from .video_processing import analyze_video
from .json_utils import parse_json_input, format_json_output, parse_video_json_input, format_video_json_output
from .image_processing import process_multiple_images, convert_image_to_base64, ProcessedImage
from .claude_integration import claude_vision_analysis
from .advanced_features import visual_judge, image_evolution_analyzer, persona_based_analysis, comparative_time_series_analysis, generate_alt_text, AnalysisParams, OutputType
from .config import CONFIG, save_config

class ClaudeVisionError(Exception):
    pass

@click.group()
def cli():
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
def analyze(input_file: Optional[str], persona: Optional[str], json_input: Optional[click.File], output: str,
            stream: bool, video: bool, frame_interval: int, num_workers: Optional[int], prompt: Optional[str],
            system: Optional[str], prefill: Optional[str], max_tokens: int, group: bool):
    if not input_file and not sys.stdin.isatty():
        input_data = sys.stdin.buffer.read()
        input_file = io.BytesIO(input_data)
    asyncio.run(claude_vision_async(input_file, persona, json_input, output, stream, video, frame_interval,
                                    num_workers, prompt, system, prefill, max_tokens, group))

async def claude_vision_async(input_file: Union[str, io.BytesIO], persona: Optional[str], json_input: Optional[click.File],
                              output: str, stream: bool, video: bool, frame_interval: int, num_workers: Optional[int],
                              prompt: Optional[str], system: Optional[str], prefill: Optional[str], max_tokens: int, group: bool):
    try:
        data = parse_input_data(json_input, video, input_file, persona, frame_interval)
        
        if video or (isinstance(input_file, str) and is_video_file(input_file)):
            await process_video(data['input_file'], data['frame_interval'], data['persona'], output, stream, num_workers, prompt, system, group)
        else:
            await process_image(data['input_file'], data['persona'], output, stream, prompt, system, prefill, max_tokens, group)

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
    processed_images = await get_base64_images(input_file, group)
    prompt = prompt or generate_prompt(persona)

    result = await claude_vision_analysis(
        [img.base64 for img in processed_images],  # Extract base64 strings
        prompt,
        output,
        stream,
        system=system,
        max_tokens=max_tokens,
        prefill=prefill
    )
    await output_result(result, output, stream)

async def get_base64_images(input_file, group):
    if isinstance(input_file, io.BytesIO):
        image = Image.open(input_file)
        return [ProcessedImage(base64=convert_image_to_base64(image), estimated_tokens=estimate_image_tokens(image))]
    return await process_multiple_images([input_file], process_as_group=group)

async def output_result(result: Union[str, AsyncGenerator[str, None]], output: str, stream: bool):
    if isinstance(result, AsyncGenerator):
        result_str = ""
        async for chunk in result:
            result_str += chunk
        result = result_str

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

def generate_prompt(persona=None):
    base_prompt = "Analyze this image and provide a detailed description."
    if persona:
        return f"As a {persona}, {base_prompt}"
    return base_prompt

@cli.command()
@click.argument('image_paths', nargs=-1, type=click.Path(exists=True), required=True)
@click.option('--criteria', required=True, help="Comma-separated list of criteria")
@click.option('--weights', required=True, help="Comma-separated list of weights")
@click.option('--output', type=click.Choice(['json', 'md', 'markdown', 'text']), default='text', help="Output format")
@click.option('--prompt', help="Custom prompt for judging")
def judge(image_paths, criteria, weights, output, prompt):
    if len(image_paths) < 2:
        raise click.UsageError("At least two images are required for judging.")
    
    criteria_list = criteria.split(',')
    weights_list = [float(w) for w in weights.split(',')]
    
    if len(criteria_list) != len(weights_list):
        raise click.UsageError("Number of criteria must match number of weights.")
    
    asyncio.run(judge_async(image_paths, criteria_list, weights_list, output, prompt))

async def judge_async(image_paths, criteria, weights, output, prompt):
    try:
        base64_images = await process_multiple_images(image_paths)
        result = await visual_judge(base64_images, criteria, weights, output, False, prompt)
        click.echo(result)
    except Exception as e:
        click.echo(f"An error occurred during judging: {str(e)}", err=True)
        
@cli.command()
@click.argument('image_paths', nargs=-1, type=click.Path(exists=True), required=True)
@click.option('--time-points', required=True, help="Comma-separated list of time points")
@click.option('--output', type=click.Choice(['json', 'md', 'markdown', 'text']), default='text', help="Output format")
@click.option('--prompt', help="Custom prompt for evolution analysis")
def evolution(image_paths, time_points, output, prompt):
    if len(image_paths) < 2:
        raise click.UsageError("At least two images are required for evolution analysis.")
    
    time_points_list = time_points.split(',')
    
    if len(image_paths) != len(time_points_list):
        raise click.UsageError("Number of images must match number of time points.")
    
    asyncio.run(evolution_async(image_paths, time_points_list, output, prompt))

async def evolution_async(image_paths, time_points, output, prompt):
    try:
        processed_images = await process_multiple_images(image_paths)
        params = AnalysisParams(
            base64_images=[img.base64 for img in processed_images],
            output_type=OutputType[output.upper()],
            stream=False,
            user_prompt=prompt
        )
        result_generator = await image_evolution_analyzer(params, time_points)
        result = ""
        async for chunk in result_generator:
            result += chunk
        await output_result(result, output, False)
    except Exception as e:
        click.echo(f"An error occurred during evolution analysis: {str(e)}", err=True)

@cli.command()
@click.argument('image_path', type=click.Path(exists=True), required=True)
@click.option('--persona', required=True, help="Professional persona to adopt")
@click.option('--output', type=click.Choice(['json', 'md', 'markdown', 'text']), default='text', help="Output format")
@click.option('--prompt', help="Custom prompt for persona-based analysis")
def persona(image_path, persona, output, prompt):
    asyncio.run(persona_async(image_path, persona, output, prompt))

async def persona_async(image_path, persona, output, prompt):
    try:
        processed_image = await process_multiple_images([image_path])
        params = AnalysisParams(
            base64_images=[img.base64 for img in processed_image],
            output_type=OutputType[output.upper()],
            stream=False,
            user_prompt=prompt
        )
        result_generator = await persona_based_analysis(params, persona)
        result = ""
        async for chunk in result_generator:
            result += chunk
        await output_result(result, output, False)
    except Exception as e:
        click.echo(f"An error occurred during persona-based analysis: {str(e)}", err=True)

@cli.command()
@click.argument('image_paths', nargs=-1, type=click.Path(exists=True), required=True)
@click.option('--time-points', required=True, help="Comma-separated list of time points")
@click.option('--metrics', required=True, help="Comma-separated list of metrics to analyze")
@click.option('--output', type=click.Choice(['json', 'md', 'markdown', 'text']), default='text', help="Output format")
@click.option('--prompt', help="Custom prompt for time-series analysis")
def time_series(image_paths, time_points, metrics, output, prompt):
    if len(image_paths) < 2:
        raise click.UsageError("At least two images are required for time series analysis.")
    
    time_points_list = time_points.split(',')
    metrics_list = metrics.split(',')
    
    if len(image_paths) != len(time_points_list):
        raise click.UsageError("Number of images must match number of time points.")
    
    asyncio.run(time_series_async(image_paths, time_points_list, metrics_list, output, prompt))

async def time_series_async(image_paths, time_points, metrics, output, prompt):
    try:
        processed_images = await process_multiple_images(image_paths)
        params = AnalysisParams(
            base64_images=[img.base64 for img in processed_images],
            output_type=OutputType[output.upper()],
            stream=False,
            user_prompt=prompt
        )
        result_generator = await comparative_time_series_analysis(params, time_points, metrics)
        result = ""
        async for chunk in result_generator:
            result += chunk
        await output_result(result, output, False)
    except Exception as e:
        click.echo(f"An error occurred during time series analysis: {str(e)}", err=True)

@cli.command()
@click.argument('image_path', type=click.Path(exists=True), required=True)
@click.option('--output', type=click.Choice(['json', 'md', 'markdown', 'text']), default='text', help="Output format")
@click.option('--prompt', help="Custom prompt for alt-text generation")
def alt_text(image_path, output, prompt):
    asyncio.run(alt_text_async(image_path, output, prompt))

async def alt_text_async(image_path, output, prompt):
    try:
        processed_image = await process_multiple_images([image_path])
        params = AnalysisParams(
            base64_images=[img.base64 for img in processed_image],
            output_type=OutputType[output.upper()],
            stream=False,
            user_prompt=prompt
        )
        result_generator = await generate_alt_text(params)
        result = ""
        async for chunk in result_generator:
            result += chunk
        await output_result(result, output, False)
    except Exception as e:
        click.echo(f"An error occurred during alt-text generation: {str(e)}", err=True)

@cli.command()
@click.option('--key', help="Config key to set or get")
@click.option('--value', help="Value to set for the config key")
def config(key, value):
    """Manage Claude Vision configuration."""
    if key and value:
        CONFIG[key] = value
        save_config(CONFIG)
        click.echo(f"Set {key} to {value}")
    elif key:
        click.echo(f"{key}: {CONFIG.get(key, 'Not set')}")
    else:
        for k, v in CONFIG.items():
            click.echo(f"{k}: {v}")

if __name__ == '__main__':
    cli()
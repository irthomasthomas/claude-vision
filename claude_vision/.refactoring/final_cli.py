from typing import AsyncGenerator, List
import click
import json
import asyncio
from .claude_integration import claude_vision_analysis
from .json_utils import parse_json_input, format_json_output
from .image_processing import process_multiple_images
from .advanced_features import visual_judge, image_evolution_analyzer, comparative_time_series_analysis
from .video_utils import is_video_file, extract_frames, get_video_metadata

@click.group()
def cli():
    pass

@cli.command()
@click.argument('input_file', type=click.Path(exists=True), required=False)
@click.option('--persona', help="Optional persona for analysis")
@click.option('--json-input', type=click.File('r'), help="JSON input for chained operations")
@click.option('--output', type=click.Choice(['json', 'md', 'markdown', 'text']), default='text', help="Output format")
@click.option('--stream', is_flag=True, help="Stream the response in real-time")
@click.option('--tools', multiple=True, help="Specify tools to use during analysis")
@click.option('--prefill', help="Set initial content for the analysis")
@click.option('--prompt', help="Specify a custom prompt for the analysis")
@click.option('--system-prompt', help="Specify a custom system-level prompt")
@click.option('--num-workers', type=int, default=1, help="Number of worker threads/processes to use")
@click.option('--frame-interval', type=int, default=30, help="Interval for extracting frames from video")
def analyze(input_file, persona, json_input, output, stream, tools, prefill, prompt, system_prompt, num_workers, frame_interval):
    asyncio.run(claude_vision_async(input_file, persona, json_input, output, stream, tools, prefill, prompt, system_prompt, num_workers, frame_interval))

@cli.command()
@click.argument('image_paths', nargs=-1, type=click.Path(exists=True), required=True)
@click.option('--criteria', required=True, help="Comma-separated list of criteria")
@click.option('--weights', required=True, help="Comma-separated list of weights")
@click.option('--output', type=click.Choice(['json', 'md', 'markdown', 'text']), default='text', help="Output format")
def judge(image_paths, criteria, weights, output):
    if len(image_paths) < 2:
        raise click.UsageError("At least two images are required for judging.")
    
    criteria_list = criteria.split(',')
    weights_list = [float(w) for w in weights.split(',')]
    
    if len(criteria_list) != len(weights_list):
        raise click.UsageError("Number of criteria must match number of weights.")
    
    asyncio.run(judge_async(image_paths, criteria_list, weights_list, output))

@cli.command()
@click.argument('image_paths', nargs=-1, type=click.Path(exists=True), required=True)
@click.option('--time-points', required=True, help="Comma-separated list of time points")
@click.option('--output', type=click.Choice(['json', 'md', 'markdown', 'text']), default='text', help="Output format")
def evolution(image_paths, time_points, output):
    if len(image_paths) < 2:
        raise click.UsageError("At least two images are required for evolution analysis.")
    
    time_points_list = time_points.split(',')
    
    if len(image_paths) != len(time_points_list):
        raise click.UsageError("Number of images must match number of time points.")
    
    asyncio.run(evolution_async(image_paths, time_points_list, output))

@cli.command()
@click.argument('image_paths', nargs=-1, type=click.Path(exists=True), required=True)
@click.option('--time-points', required=True, help="Comma-separated list of time points")
@click.option('--metrics', required=True, help="Comma-separated list of metrics to analyze")
@click.option('--output', type=click.Choice(['json', 'md', 'markdown', 'text']), default='text', help="Output format")
def time_series(image_paths, time_points, metrics, output):
    if len(image_paths) < 2:
        raise click.UsageError("At least two images are required for time series analysis.")
    
    time_points_list = time_points.split(',')
    metrics_list = metrics.split(',')
    
    if len(image_paths) != len(time_points_list):
        raise click.UsageError("Number of images must match number of time points.")
    
    asyncio.run(time_series_async(image_paths, time_points_list, metrics_list, output))

async def claude_vision_async(input_file, persona, json_input, output, stream, tools, prefill, prompt, system_prompt, num_workers, frame_interval):
    try:
        if json_input:
            data = parse_json_input(json_input)
            input_file = data['file_path']
            persona = data.get('persona', persona)
            analysis_type = data['analysis_type']
        elif not input_file:
            raise click.UsageError("Please provide an input file or JSON input.")

        if is_video_file(input_file):
            frames = extract_frames(input_file, frame_interval)
            base64_images = await process_multiple_images(frames, num_workers)
        else:
            base64_images = await process_multiple_images([input_file], num_workers)

        generated_prompt = generate_prompt(persona, prompt)
        
        result = await claude_vision_analysis(
            base64_images, 
            generated_prompt, 
            output, 
            stream, 
            system_prompt=system_prompt,
            prefill=prefill,
            tools=[{"type": tool} for tool in tools]
        )

        handle_output(result, output, stream)

    except ValueError as e:
        click.echo(f"Error: {str(e)}", err=True)
    except Exception as e:
        click.echo(f"An unexpected error occurred: {str(e)}", err=True)

async def judge_async(image_paths, criteria, weights, output):
    try:
        base64_images = await process_multiple_images(image_paths)
        result = await visual_judge(base64_images, criteria, weights, output, False)
        handle_output(result, output, False, "judge")
    except Exception as e:
        click.echo(f"An error occurred during judging: {str(e)}", err=True)

async def evolution_async(image_paths, time_points, output):
    try:
        base64_images = await process_multiple_images(image_paths)
        result = await image_evolution_analyzer(base64_images, time_points, output, False)
        handle_output(result, output, False, "evolution")
    except Exception as e:
        click.echo(f"An error occurred during evolution analysis: {str(e)}", err=True)

async def time_series_async(image_paths, time_points, metrics, output):
    try:
        base64_images = await process_multiple_images(image_paths)
        result = await comparative_time_series_analysis(base64_images, time_points, metrics, output, False)
        handle_output(result, output, False, "time_series")
    except Exception as e:
        click.echo(f"An error occurred during time series analysis: {str(e)}", err=True)

def generate_prompt(persona=None, custom_prompt=None):
    if custom_prompt:
        return custom_prompt
    base_prompt = "Analyze this image and provide a detailed description."
    if persona:
        return f"As a {persona}, {base_prompt}"
    return base_prompt

def handle_output(result, output, stream, analysis_type="description"):
    if output == 'json':
        handle_json_output(result, stream, analysis_type)
    elif output in ['md', 'markdown']:
        handle_markdown_output(result, stream)
    else:
        handle_text_output(result, stream)

async def handle_json_output(result, stream, analysis_type):
    if stream:
        async for chunk in result:
            click.echo(chunk, nl=False)
        click.echo()
    else:
        click.echo(json.dumps(format_json_output(result, analysis_type), indent=2))

async def handle_markdown_output(result, stream):
    if stream:
        async for chunk in result:
            click.echo(chunk, nl=False)
        click.echo()
    else:
        click.echo(result)

async def handle_text_output(result, stream):
    if stream:
        async for chunk in result:
            click.echo(chunk, nl=False)
        click.echo()
    else:
        click.echo(result)

if __name__ == '__main__':
    cli()
import io
import sys
from typing import AsyncGenerator
import click
import json
import asyncio
from .claude_integration import claude_vision_analysis
from .json_utils import parse_json_input, format_json_output, parse_video_json_input, format_video_json_output
from .image_processing import process_multiple_images
from .advanced_features import visual_judge, image_evolution_analyzer, comparative_time_series_analysis
from .video_processing import analyze_video
from .video_utils import is_video_file

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
def analyze(input_file, persona, json_input, output, stream, video, frame_interval, num_workers, prompt, system, prefill, max_tokens, group):
    if not input_file and not sys.stdin.isatty():
        input_data = sys.stdin.buffer.read()
        input_file = io.BytesIO(input_data)
    asyncio.run(claude_vision_async(input_file, persona, json_input, output, stream, video, frame_interval, num_workers, prompt, system, prefill, max_tokens, group))
    

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


async def claude_vision_async(input_file, persona, json_input, output, stream, video, frame_interval, num_workers, prompt, system, prefill, max_tokens, group):
    try:
        if json_input:
            data = parse_video_json_input(json_input) if video else parse_json_input(json_input)
            input_file = data['file_path']
            persona = data.get('persona', persona)
            analysis_type = data['analysis_type']
            frame_interval = data.get('frame_interval', frame_interval)
        elif not input_file:
            raise click.UsageError("Please provide an input file, pipe input, or JSON input.")

        if video or (isinstance(input_file, str) and is_video_file(input_file)):
            metadata, frame_results = await analyze_video(input_file, frame_interval, persona, output, stream, num_workers, prompt=prompt, system=system, process_as_group=group)
            
            if output == 'json':
                formatted_result = format_video_json_output(metadata, frame_results, "video_description")
                click.echo(json.dumps(formatted_result, indent=2, ensure_ascii=False))
            else:
                for result in frame_results:
                    click.echo(f"Frame {result['frame_number']} ({result['timestamp']:.2f}s): {result['result']}")
        else:
            if isinstance(input_file, io.BytesIO):
                image = Image.open(input_file)
                base64_images = [convert_image_to_base64(image)]
            else:
                base64_images = await process_multiple_images([input_file], process_as_group=group)
            if not prompt:
                prompt = generate_prompt(persona)

            result = await claude_vision_analysis(
                base64_images, prompt, output, stream, 
                system_prompt=system, 
                max_tokens=max_tokens, 
                prefill=prefill
            )
            if output == 'json':
                if stream:
                    async for chunk in result:
                        click.echo(chunk, nl=False)
                    click.echo()
                else:
                    formatted_result = format_json_output(result, "description")
                    click.echo(json.dumps(formatted_result, indent=2, ensure_ascii=False))
            elif output in ['md', 'markdown']:
                if stream:
                    async for chunk in result:
                        click.echo(chunk, nl=False)
                    click.echo()
                else:
                    click.echo(result)
            else:
                if stream:
                    async for chunk in result:
                        click.echo(chunk, nl=False)
                    click.echo()
                else:
                    click.echo(result)

    except ValueError as e:
        click.echo(f"Error: {str(e)}", err=True)
    except Exception as e:
        click.echo(f"An unexpected error occurred: {str(e)}", err=True)
                        

async def judge_async(image_paths, criteria, weights, output):
    try:
        base64_images = await process_multiple_images(image_paths)
        result = await visual_judge(base64_images, criteria, weights, output, False)
        
        if output == 'json':
            if isinstance(result, AsyncGenerator):
                full_result = ''
                async for chunk in result:
                    full_result += chunk
                click.echo(json.dumps(format_json_output(full_result, "judge"), indent=2))
            else:
                click.echo(json.dumps(format_json_output(result, "judge"), indent=2))
        elif output in ['md', 'markdown']:
            if isinstance(result, AsyncGenerator):
                async for chunk in result:
                    click.echo(chunk, nl=False)
                click.echo()
            else:
                click.echo(result)
        else:
            if isinstance(result, AsyncGenerator):
                async for chunk in result:
                    click.echo(chunk, nl=False)
                click.echo()
            else:
                click.echo(result)
    except Exception as e:
        click.echo(f"An error occurred during judging: {str(e)}", err=True)
     
        
async def evolution_async(image_paths, time_points, output):
    try:
        base64_images = await process_multiple_images(image_paths)
        result = await image_evolution_analyzer(base64_images, time_points, output, False)
        
        if output == 'json':
            click.echo(json.dumps(format_json_output(result, "evolution"), indent=2))
        elif output in ['md', 'markdown']:
            click.echo(result)
        else:
            click.echo(result)
    except Exception as e:
        click.echo(f"An error occurred during evolution analysis: {str(e)}", err=True)


async def time_series_async(image_paths, time_points, metrics, output):
    try:
        base64_images = await process_multiple_images(image_paths)
        result = await comparative_time_series_analysis(base64_images, time_points, metrics, output, False)
        
        if output == 'json':
            click.echo(json.dumps(format_json_output(result, "time_series"), indent=2))
        elif output in ['md', 'markdown']:
            click.echo(result)
        else:
            click.echo(result)
    except Exception as e:
        click.echo(f"An error occurred during time series analysis: {str(e)}", err=True)


def generate_prompt(persona=None):
    base_prompt = "Analyze this image and provide a detailed description."
    if persona:
        return f"As a {persona}, {base_prompt}"
    return base_prompt


if __name__ == '__main__':
    cli()
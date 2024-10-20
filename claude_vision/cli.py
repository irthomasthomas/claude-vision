import sys
import io
from PIL import Image
import json
from typing import AsyncGenerator
import click
import asyncio
from .video_utils import is_video_file
from .video_processing import analyze_video
from .json_utils import parse_json_input, format_json_output, parse_video_json_input, format_video_json_output
from .image_processing import process_multiple_images, convert_image_to_base64
from .claude_integration import claude_vision_analysis
from .advanced_features import visual_judge, image_evolution_analyzer, persona_based_analysis, comparative_time_series_analysis, generate_alt_text
from .config import CONFIG, save_config

@click.group()
def cli():
    pass

@cli.command()
@click.argument('input_files', nargs=-1, type=click.Path(exists=True), required=False)
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
@click.option('--multi-angle', is_flag=True, help="Treat multiple images as different angles of the same object")
@click.option('--multi-object', is_flag=True, help="Treat multiple images as different objects")
def analyze(input_files, persona, json_input, output, stream, video, frame_interval, num_workers, prompt, system, prefill, max_tokens, group, multi_angle, multi_object):
    if not input_files and not sys.stdin.isatty():
        input_data = sys.stdin.buffer.read()
        input_files = [io.BytesIO(input_data)]
    asyncio.run(claude_vision_async(input_files, persona, json_input, output, stream, video, frame_interval, num_workers, prompt, system, prefill, max_tokens, group, multi_angle, multi_object))

async def claude_vision_async(input_files, persona, json_input, output, stream, video, frame_interval, num_workers, prompt, system, prefill, max_tokens, group, multi_angle, multi_object):
    try:
        if json_input:
            data = parse_video_json_input(json_input) if video else parse_json_input(json_input)
            input_files = [data['file_path']]
            persona = data.get('persona', persona)
            analysis_type = data['analysis_type']
            frame_interval = data.get('frame_interval', frame_interval)
        elif not input_files:
            raise click.UsageError("Please provide input files, pipe input, or JSON input.")

        if video or (isinstance(input_files[0], str) and is_video_file(input_files[0])):
            metadata, frame_results = await analyze_video(input_files[0], frame_interval, persona, output, stream, num_workers, prompt=prompt, system=system, process_as_group=group)
            
            if output == 'json':
                formatted_result = format_video_json_output(metadata, frame_results, "video_description")
                click.echo(json.dumps(formatted_result, indent=2, ensure_ascii=False))
            else:
                for result in frame_results:
                    click.echo(f"Frame {result['frame_number']} ({result['timestamp']:.2f}s): {result['result']}")
        else:
            if all(isinstance(file, io.BytesIO) for file in input_files):
                base64_images = [convert_image_to_base64(Image.open(file)) for file in input_files]
            else:
                base64_images = await process_multiple_images(input_files, process_as_group=group)
            
            if not prompt:
                prompt = generate_prompt(persona, multi_angle, multi_object, len(base64_images))

            result = await claude_vision_analysis(
                base64_images, prompt, output, stream, 
                system=system, 
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

def generate_prompt(persona=None, multi_angle=False, multi_object=False, num_images=1):
    if num_images == 1:
        base_prompt = "Analyze this image and provide a detailed description."
    else:
        if multi_angle:
            base_prompt = f"Analyze these {num_images} images as different angles of the same object. Provide a detailed description of the object based on all angles."
        elif multi_object:
            base_prompt = f"Analyze these {num_images} images as different objects. Provide a detailed description of each object separately."
        else:
            base_prompt = f"Analyze these {num_images} images and provide a detailed description for each."

    if persona:
        return f"As a {persona}, {base_prompt}"
    return base_prompt

# ... (rest of the file content)


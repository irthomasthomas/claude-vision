import json
import click
import sys
from PIL import Image, UnidentifiedImageError
from io import BytesIO
from .image_processing import process_image
from .claude_integration import claude_vision_analysis
from .config import DEFAULT_PROMPT, CONFIG
from .utils import logger
from .advanced_features import (
    visual_judge,
    image_evolution_analyzer,
    persona_based_analysis,
    comparative_time_series_analysis,
    generate_alt_text
)

# Todo: Try to streamline the cli user experience.
# allow --stream option for all modes

# The following use cases should work:
# claude-vision image.jpg 
    #   - describe a local image
# claude-vision image.jpg https://en.wikimedia.org/wiki/File:Example.jpg --text --json # jq .[] | .filename, .url, .description, .tokens # or whatever the API returns.
    #   - describe a local image and a remote image independentaly and return the basic text descriptions in a json object.
# Text-to-speech use-case:
# claude-vision ocr screen --output json --schema '{"filename": "", "text": ""}' | jq .[] | .text | espeak
#   --default-prompt " <INST>Study the image carefuly. If there is text present, write the text exactly. Otherwise, if NO text is visible, return an empty string. Read the text on the screenshot image. Replace high entropy strings with a placeholder.</INST"}'

# scrot -s - | claude-vision - -p "read the urls in this image and write one per line. Say nothing else except a single url per line." | xargs -I {} xdotool type {}

# claude-vision evolution image_1.png image_2.png image_3.png

# claude-vision plugins

# claude-vision personas

# Ideas:
# Multi-Modal System Prompts.
# - I am not sure if this makes sense yet, need to scan docs. 
# - Thought about including few-shot style sample images with descriptions - 
# - e.g. geometry textbook images followed by their description to enhance spatial reasoning. such as geometry texts
# Grid search
# Cost calculator
# Simulator
# Depict the croping of an image in ascii (if relevant)


@click.group()
def cli():
    """Claude Vision CLI for advanced image analysis."""
    pass

@cli.command()
@click.argument('image_sources', nargs=-1, type=click.Path(exists=True), required=False)
@click.option('-p', '--prompt', default=DEFAULT_PROMPT, help="Prompt for the vision model")
@click.option('--output', type=click.Choice(['text', 'json', 'md'], case_sensitive=False), default='text')
@click.option('--stream', is_flag=True, help="Stream the response in real-time")
@click.option('--max-tokens', type=int, default=1000, help="Maximum number of tokens in the response")
@click.option('--system-prompt', help="Custom system prompt for Claude")
def analyze(image_sources, prompt, output, stream, max_tokens, system_prompt):
    """Analyze images using Claude 3.5 Sonnet vision model."""
    if not image_sources and not sys.stdin.isatty():
        # Read image from stdin
        image_data = sys.stdin.buffer.read()
        if not image_data:
            click.echo("Error: No image data received from stdin.", err=True)
            sys.exit(1)
        try:
            image = Image.open(BytesIO(image_data))
            images_to_process = [("stdin", image)]
        except UnidentifiedImageError:
            click.echo("Error: Unable to identify image from stdin. No valid image data received.", err=True)
            sys.exit(1)
    elif not image_sources:
        click.echo("Error: No image sources provided. Please specify image files or pipe an image to stdin.", err=True)
        sys.exit(1)
    else:
        images_to_process = [(source, source) for source in image_sources]

    process_images(images_to_process, prompt, output, stream, max_tokens, system_prompt)
    
@cli.command()
@click.argument('image_paths', nargs=-1, type=click.Path(exists=True), required=True)
@click.option('--criteria', required=True, help="Comma-separated list of criteria for comparison")
@click.option('--weights', required=True, help="Comma-separated list of weights for each criterion")
@click.option('--output', type=click.Choice(['text', 'json', 'md'], case_sensitive=False), default='text')
def judge(image_paths, criteria, weights, output):
    """judge and rank multiple images based on given criteria."""
    # Todo: add --stream option
    base64_images = [process_image(path) for path in image_paths]
    criteria_list = [c.strip() for c in criteria.split(',')]
    weights_list = [float(w.strip()) for w in weights.split(',')]
    
    result = visual_judge(base64_images, criteria_list, weights_list, output)
    click.echo(result)



@cli.command()
@click.argument('image_paths', nargs=-1, type=click.Path(exists=True), required=True)
@click.option('--time-points', required=True, help="Comma-separated list of time points for each image")
@click.option('--output', type=click.Choice(['text', 'json', 'md'], case_sensitive=False), default='text')
def evolution(image_paths, time_points, output):
    """Analyze a series of images to describe changes over time."""
    # Todo: add --stream option
    base64_images = [process_image(path) for path in image_paths]
    time_points_list = [t.strip() for t in time_points.split(',')]
    
    result = image_evolution_analyzer(base64_images, time_points_list, output)
    click.echo(result)


@cli.command()
@click.argument('image_path', type=click.Path(exists=True), required=True)
@click.option('--persona', required=True, help="Professional persona to adopt")
@click.option('--style', required=True, help="Stylistic persona to adopt")
@click.option('--output', type=click.Choice(['text', 'json', 'md'], case_sensitive=False), default='text')
def persona(image_path, persona, style, output):
    """Analyze an image using a specified professional and stylistic persona."""
    base64_image = process_image(image_path)
    
    result = persona_based_analysis(base64_image, persona, style, output)
    click.echo(result)

@cli.command()
@click.argument('image_paths', nargs=-1, type=click.Path(exists=True), required=True)
@click.option('--time-points', required=True, help="Comma-separated list of time points for each image")
@click.option('--metrics', required=True, help="Comma-separated list of metrics to analyze")
@click.option('--output', type=click.Choice(['text', 'json', 'md'], case_sensitive=False), default='text')
def time_series(image_paths, time_points, metrics, output):
    """Perform comparative time-series analysis on multiple images."""
    # Todo: add --stream option
    base64_images = [process_image(path) for path in image_paths]
    time_points_list = [t.strip() for t in time_points.split(',')]
    metrics_list = [m.strip() for m in metrics.split(',')]
    
    result = comparative_time_series_analysis(base64_images, time_points_list, metrics_list, output)
    click.echo(result)


@cli.command()
@click.argument('image_path', type=click.Path(exists=True), required=True)
@click.option('--output', type=click.Choice(['text', 'json', 'md'], case_sensitive=False), default='text')
def alt_text(image_path, output):
    """Generate detailed, context-aware alt-text for an image."""
    base64_image = process_image(image_path)
    
    result = generate_alt_text(base64_image, output)
    click.echo(result)


def process_images(images_to_process, prompt, output, stream, max_tokens, system_prompt):    
    base64_images = []
    for source, img_source in images_to_process:
        try:
            base64_image = process_image(img_source)
            base64_images.append(base64_image)
        except Exception as e:
            logger.error(f"Error processing image {source}: {str(e)}")
    try:
        result = claude_vision_analysis(base64_images, prompt, output, stream, system_prompt, max_tokens)
        if stream:
            for line in result:
                try:
                    event = json.loads(line.decode('utf-8').strip('data: '))
                    if event['type'] == 'content_block_delta':
                        text = event['delta'].get('text', '')
                        click.echo(text, nl=False)
                    elif event['type'] == 'message_stop':
                        click.echo()  # Add a newline at the end
                except json.JSONDecodeError:
                    pass  # Ignore non-JSON lines (like 'ping' events)
        else:
            if output == 'json':
                result = json.dumps(json.loads(result), indent=2)
            click.echo(result)
    except Exception as e:
        logger.error(f"Error analyzing images: {str(e)}")
        
        
if __name__ == '__main__':
    cli()
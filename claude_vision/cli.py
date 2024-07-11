import json
import click
import sys
from PIL import Image
from .image_processing import process_image
from .claude_integration import claude_vision_analysis
from .config import DEFAULT_PROMPT, CONFIG
from .utils import logger
from .advanced_features import (
    visual_decider,
    image_evolution_analyzer,
    persona_based_analysis,
    comparative_time_series_analysis,
    generate_alt_text
)

@click.group()
def cli():
    pass

@cli.command()
@click.argument('image_paths', nargs=-1, type=click.Path(exists=True), required=True)
@click.option('--criteria', required=True, help="Comma-separated list of criteria for comparison")
@click.option('--weights', required=True, help="Comma-separated list of weights for each criterion")
def decide(image_paths, criteria, weights):
    """Compare and rank multiple images based on given criteria."""
    base64_images = [process_image(path) for path in image_paths]
    criteria_list = [c.strip() for c in criteria.split(',')]
    weights_list = [float(w.strip()) for w in weights.split(',')]
    
    result = visual_decider(base64_images, criteria_list, weights_list)
    click.echo(result)

@cli.command()
@click.argument('image_paths', nargs=-1, type=click.Path(exists=True), required=True)
@click.option('--time-points', required=True, help="Comma-separated list of time points for each image")
def evolution(image_paths, time_points):
    """Analyze a series of images to describe changes over time."""
    base64_images = [process_image(path) for path in image_paths]
    time_points_list = [t.strip() for t in time_points.split(',')]
    
    result = image_evolution_analyzer(base64_images, time_points_list)
    click.echo(result)

@cli.command()
@click.argument('image_path', type=click.Path(exists=True), required=True)
@click.option('--persona', required=True, help="Professional persona to adopt")
@click.option('--style', required=True, help="Stylistic persona to adopt")
def persona_analysis(image_path, persona, style):
    """Analyze an image using a specified professional and stylistic persona."""
    base64_image = process_image(image_path)
    
    result = persona_based_analysis(base64_image, persona, style)
    click.echo(result)

@cli.command()
@click.argument('image_paths', nargs=-1, type=click.Path(exists=True), required=True)
@click.option('--time-points', required=True, help="Comma-separated list of time points for each image")
@click.option('--metrics', required=True, help="Comma-separated list of metrics to analyze")
def time_series(image_paths, time_points, metrics):
    """Perform comparative time-series analysis on multiple images."""
    base64_images = [process_image(path) for path in image_paths]
    time_points_list = [t.strip() for t in time_points.split(',')]
    metrics_list = [m.strip() for m in metrics.split(',')]
    
    result = comparative_time_series_analysis(base64_images, time_points_list, metrics_list)
    click.echo(result)

@cli.command()
@click.argument('image_path', type=click.Path(exists=True), required=True)
def alt_text(image_path):
    """Generate detailed, context-aware alt-text for an image."""
    base64_image = process_image(image_path)
    
    result = generate_alt_text(base64_image)
    click.echo(result)

@cli.command()
@click.argument('image_paths', nargs=-1, type=click.Path(exists=True), required=False)
@click.option('-u', '--url', help="URL of an image to analyze")
@click.option('-p', '--prompt', default=DEFAULT_PROMPT, help="Prompt for the vision model")
@click.option('--output', type=click.Choice(['text', 'json', 'md'], case_sensitive=False), default='text')
@click.option('--stream', is_flag=True, help="Stream the response in real-time")
@click.option('--max-tokens', type=int, default=1000, help="Maximum number of tokens in the response")
@click.option('--system-prompt', help="Custom system prompt for Claude")
def analyze(image_paths, url, prompt, output, stream, max_tokens, system_prompt):
    """Analyze images using Claude 3.5 Sonnet vision model."""
    if not image_paths and not url and not sys.stdin.isatty():
        image = Image.open(sys.stdin.buffer)
        images_to_process = [("stdin", image)]
    elif not image_paths and not url:
        click.echo("Error: Please provide either image paths, a URL, or pipe an image.")
        sys.exit(1)
    else:
        images_to_process = []
        if url:
            images_to_process.append((url, url))
        for image_path in image_paths:
            images_to_process.append((image_path, image_path))

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
            click.echo(result)
    except Exception as e:
        logger.error(f"Error analyzing images: {str(e)}")

if __name__ == '__main__':
    cli()
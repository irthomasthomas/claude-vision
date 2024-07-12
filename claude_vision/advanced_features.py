from .claude_integration import claude_vision_analysis
from .config import DEFAULT_PERSONAS, DEFAULT_STYLES

# Todo: Some of these features would be better as prompt templates or plugins. So we can expand the behaviour easier.
# Todo: Claude Prefil: Use prefil to
#   - guarantee an json object for json 
#   - reduce refusals
#   - 
# Todo: Function calling api could be re-used to improve json output, (use function calling api to define schemas )

def visual_judge(base64_images, criteria, weights, output_type):
    """
    Judge and rank multiple images based on user-defined criteria and weights.
    """
    prompt = f"Judge the following images based on these criteria: {criteria}. "
    prompt += f"Use these weights for each criterion: {weights}. "
    prompt += "Provide a structured comparison, ranking, and declare a winner."

    result = claude_vision_analysis(base64_images, prompt, output_type)
    return result

def image_evolution_analyzer(base64_images, time_points, output_type):
    """
    Analyze a series of images to describe changes over time.
    """
    prompt = "Analyze the following series of images and describe the changes over time. "
    prompt += f"The images correspond to these time points: {time_points}. "
    prompt += "Provide a detailed analysis of the evolution observed in the images."

    result = claude_vision_analysis(base64_images, prompt, output_type)
    return result

def persona_based_analysis(base64_image, persona, style, output_type):
    """
    Analyze an image using a specified professional persona and stylistic persona.
    """
    system_prompt = f"{DEFAULT_PERSONAS.get(persona, '')} {DEFAULT_STYLES.get(style, '')}"
    prompt = "Analyze the following image in character, combining your professional expertise with the specified style."

    result = claude_vision_analysis([base64_image], prompt, output_type, system_prompt=system_prompt)
    return result

def comparative_time_series_analysis(base64_images, time_points, metrics, output_type):
    """
    Analyze multiple images to identify trends, anomalies, or patterns across a dataset with a temporal dimension.
    """
    prompt = f"Analyze the following series of images taken at these time points: {time_points}. "
    prompt += f"Focus on these metrics: {metrics}. "
    prompt += "Identify trends, anomalies, or patterns across the dataset, considering the temporal dimension."

    result = claude_vision_analysis(base64_images, prompt, output_type)
    return result

def generate_alt_text(base64_image, output_type):
    """
    Generate detailed, context-aware alt-text for an image.
    """
    prompt = "Generate a detailed, context-aware alt-text for this image. "
    prompt += "Include semantic information and relevant details to improve web accessibility."

    result = claude_vision_analysis([base64_image], prompt, output_type)
    return result
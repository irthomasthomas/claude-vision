from .claude_integration import claude_vision_analysis
from .config import DEFAULT_PERSONAS, DEFAULT_STYLES

def visual_decider(base64_images, criteria, weights):
    """
    Compare multiple images based on user-defined criteria and weights.
    """
    prompt = f"Compare the following images based on these criteria: {criteria}. "
    prompt += f"Use these weights for each criterion: {weights}. "
    prompt += "Provide a structured comparison, ranking, and declare a winner."

    result = claude_vision_analysis(base64_images, prompt, 'text')
    return result

def image_evolution_analyzer(base64_images, time_points):
    """
    Analyze a series of images to describe changes over time.
    """
    prompt = "Analyze the following series of images and describe the changes over time. "
    prompt += f"The images correspond to these time points: {time_points}. "
    prompt += "Provide a detailed analysis of the evolution observed in the images."

    result = claude_vision_analysis(base64_images, prompt, 'text')
    return result

def persona_based_analysis(base64_image, persona, style):
    """
    Analyze an image using a specified professional persona and stylistic persona.
    """
    system_prompt = f"{DEFAULT_PERSONAS.get(persona, '')} {DEFAULT_STYLES.get(style, '')}"
    prompt = "Analyze the following image in character, combining your professional expertise with the specified style."

    result = claude_vision_analysis([base64_image], prompt, 'text', system_prompt=system_prompt)
    return result

def comparative_time_series_analysis(base64_images, time_points, metrics):
    """
    Analyze multiple images to identify trends, anomalies, or patterns across a dataset with a temporal dimension.
    """
    prompt = f"Analyze the following series of images taken at these time points: {time_points}. "
    prompt += f"Focus on these metrics: {metrics}. "
    prompt += "Identify trends, anomalies, or patterns across the dataset, considering the temporal dimension."

    result = claude_vision_analysis(base64_images, prompt, 'text')
    return result

def generate_alt_text(base64_image):
    """
    Generate detailed, context-aware alt-text for an image.
    """
    prompt = "Generate a detailed, context-aware alt-text for this image. "
    prompt += "Include semantic information and relevant details to improve web accessibility."

    result = claude_vision_analysis([base64_image], prompt, 'text')
    return result
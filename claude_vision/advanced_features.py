from .claude_integration import claude_vision_analysis
from .config import DEFAULT_PERSONAS, DEFAULT_STYLES
from typing import List, Dict, Any, AsyncGenerator

async def visual_judge(base64_images: List[str], criteria: List[str], weights: List[float], output_type: str, stream: bool, user_prompt: str = None) -> AsyncGenerator[str, None]:
    """
    Judge and rank multiple images based on user-defined criteria and weights.
    """

    prompt = f"Judge the following images based on these criteria: {', '.join(criteria)}. "
    prompt += f"Use these weights for each criterion: {', '.join(map(str, weights))}. "
    prompt += "Provide a structured comparison, ranking, and declare a winner."
    if user_prompt:
        prompt += f"<USER_PROMPT>{user_prompt}</USER_PROMPT>"
        
    result = await claude_vision_analysis(base64_images, prompt, output_type, stream)
    return result

async def image_evolution_analyzer(base64_images: List[str], time_points: List[str], output_type: str, stream: bool, user_prompt: str = None) -> AsyncGenerator[str, None]:
    """
    Analyze a series of images to describe changes over time.
    """
    prompt = "Analyze the following series of images and describe the changes over time. "
    prompt += f"The images correspond to these time points: {', '.join(time_points)}. "
    prompt += "Provide a detailed analysis of the evolution observed in the images."
    if user_prompt:
        prompt += f"<USER_PROMPT>{user_prompt}</USER_PROMPT>"

    result = await claude_vision_analysis(base64_images, prompt, output_type, stream)
    return result


async def comparative_time_series_analysis(base64_images: List[str], time_points: List[str], metrics: List[str], output_type: str, stream: bool, user_prompt: str = None) -> AsyncGenerator[str, None]:
    """
    Analyze multiple images to identify trends, anomalies, or patterns across a dataset with a temporal dimension.
    """
    
    prompt = f"Analyze the following series of images taken at these time points: {', '.join(time_points)}. "
    prompt += f"Focus on these metrics: {', '.join(metrics)}. "
    prompt += "Identify trends, anomalies, or patterns across the dataset, considering the temporal dimension."
    if user_prompt:
        prompt += f"<USER_NOTE>{user_prompt}</USER_NOTE>"
        
    result = await claude_vision_analysis(base64_images, prompt, output_type, stream)
    return result

async def persona_based_analysis(base64_image: str, persona: str, output_type: str, stream: bool, user_prompt: str = None) -> AsyncGenerator[str, None]:
    """
    Analyze an image using a specified professional persona.
    """
    system = f"{DEFAULT_PERSONAS.get(persona, '')}"
    
    prompt = "Analyze the following image in character, using your professional expertise."
    if user_prompt:
        prompt += f"<USER_PROMPT>{user_prompt}</USER_PROMPT>"

    result = await claude_vision_analysis([base64_image], prompt, output_type, stream, system=system)
    return result

async def generate_alt_text(base64_image: str, output_type: str, stream: bool, user_prompt: str = None) -> AsyncGenerator[str, None]:
    """
    Generate detailed, context-aware alt-text for an image.
    """
    prompt = "Generate a detailed, context-aware alt-text for this image. "
    prompt += "Include semantic information and relevant details to improve web accessibility."
    if user_prompt:
        prompt += f"<USER_NOTE>{user_prompt}</USER_NOTE>"

    result = await claude_vision_analysis([base64_image], prompt, output_type, stream)
    return result
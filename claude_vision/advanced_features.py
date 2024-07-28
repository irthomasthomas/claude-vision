from typing import List, AsyncGenerator
from enum import Enum
from dataclasses import dataclass

from .claude_integration import claude_vision_analysis
from .config import DEFAULT_PERSONAS, DEFAULT_STYLES
from .image_processing import ProcessedImage  # Add this line

class OutputType(Enum):
    JSON = "json"
    MARKDOWN = "md"
    TEXT = "text"

@dataclass
class AnalysisParams:
    base64_images: List[ProcessedImage]  # Change this from List[str] to List[ProcessedImage]
    output_type: OutputType
    stream: bool
    user_prompt: str = None
    system: str = None

async def visual_judge(base64_images: List[str], criteria: List[str], weights: List[float], output_type: str, stream: bool, user_prompt: str = None) -> str:
    """
    Judge and rank multiple images based on user-defined criteria and weights.
    """

    prompt = f"Judge the following images based on these criteria: {', '.join(criteria)}. "
    prompt += f"Use these weights for each criterion: {', '.join(map(str, weights))}. "
    prompt += "Provide a structured comparison, ranking, and declare a winner."
    if user_prompt:
        prompt += f"<USER_PROMPT>{user_prompt}</USER_PROMPT>"
        
    result = await claude_vision_analysis(base64_images, prompt, output_type, stream)
    if stream:
        return "".join([chunk async for chunk in result])
    else:
        return result

async def image_evolution_analyzer(params: AnalysisParams, time_points: List[str]) -> AsyncGenerator[str, None]:
    """Analyze a series of images to describe changes over time."""
    prompt = (
        "Analyze the following series of images and describe the changes over time. "
        f"The images correspond to these time points: {', '.join(time_points)}. "
        "Provide a detailed analysis of the evolution observed in the images."
    )
    return await _perform_analysis(params, prompt)

async def comparative_time_series_analysis(params: AnalysisParams, time_points: List[str], metrics: List[str]) -> AsyncGenerator[str, None]:
    """Analyze multiple images to identify trends, anomalies, or patterns across a dataset with a temporal dimension."""
    prompt = (
        f"Analyze the following series of images taken at these time points: {', '.join(time_points)}. "
        f"Focus on these metrics: {', '.join(metrics)}. "
        "Identify trends, anomalies, or patterns across the dataset, considering the temporal dimension."
    )
    return await _perform_analysis(params, prompt)

async def persona_based_analysis(params: AnalysisParams, persona: str) -> AsyncGenerator[str, None]:
    """Analyze an image using a specified professional persona."""
    params.system = DEFAULT_PERSONAS.get(persona, '')
    prompt = "Analyze the following image in character, using your professional expertise."
    return await _perform_analysis(params, prompt)

async def generate_alt_text(params: AnalysisParams) -> AsyncGenerator[str, None]:
    """Generate detailed, context-aware alt-text for an image."""
    prompt = (
        "Generate a detailed, context-aware alt-text for this image. "
        "Include semantic information and relevant details to improve web accessibility."
    )
    return await _perform_analysis(params, prompt)

async def _perform_analysis(params: AnalysisParams, base_prompt: str) -> AsyncGenerator[str, None]:
    """Helper function to perform the analysis with claude_vision_analysis."""
    prompt = base_prompt
    if params.user_prompt:
        prompt += f" <USER_PROMPT>{params.user_prompt}</USER_PROMPT>"

    async for chunk in claude_vision_analysis(
        [img.base64 for img in params.base64_images],  # Extract base64 strings
        prompt,
        params.output_type.value,
        params.stream,
        system=params.system,
    ):
        yield chunk
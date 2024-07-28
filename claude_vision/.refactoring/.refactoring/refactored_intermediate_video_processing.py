from typing import List, Dict, Any, Optional, Tuple
import asyncio
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass

from .claude_integration import claude_vision_analysis
from .video_utils import get_video_metadata, extract_frames
from .image_processing import process_multiple_images
from .exceptions import VideoProcessingError

@dataclass
class VideoAnalysisResult:
    metadata: Dict[str, Any]
    frame_results: List[Dict[str, Any]]

@dataclass
class FrameAnalysisParams:
    frames: List[Dict[str, Any]]
    persona: Optional[str]
    output: str
    stream: bool
    batch_size: int
    prompt: Optional[str]
    system: Optional[str]
    process_as_group: bool

async def process_video_frames(params: FrameAnalysisParams) -> List[Dict[str, Any]]:
    try:
        base64_frames = await process_multiple_images([frame['frame'] for frame in params.frames])
        return await _process_frame_batches(params, base64_frames)
    except Exception as e:
        raise VideoProcessingError(f"Error processing video frames: {str(e)}")

async def _process_frame_batches(params: FrameAnalysisParams, base64_frames: List[str]) -> List[Dict[str, Any]]:
    async with ThreadPoolExecutor() as executor:
        tasks = [
            asyncio.create_task(_process_frame_batch(params, base64_frames[i:i+params.batch_size], i))
            for i in range(0, len(base64_frames), params.batch_size)
        ]
        batched_results = await asyncio.gather(*tasks)
    return [result for batch in batched_results for result in batch]

async def _process_frame_batch(params: FrameAnalysisParams, batch_frames: List[str], start_index: int) -> List[Dict[str, Any]]:
    frame_prompt = generate_frame_prompt(params, start_index, len(batch_frames))
    
    if params.process_as_group:
        result = await claude_vision_analysis(batch_frames, frame_prompt, params.output, params.stream, system=params.system)
        return [create_frame_result(params.frames[i], result) for i in range(start_index, start_index + len(batch_frames))]
    else:
        return [
            create_frame_result(params.frames[i], await claude_vision_analysis([frame], frame_prompt, params.output, params.stream, system=params.system))
            for i, frame in enumerate(batch_frames, start=start_index)
        ]

async def analyze_video(
    video_path: str,
    frame_interval: int,
    persona: Optional[str],
    output: str,
    stream: bool,
    num_workers: Optional[int] = None,
    prompt: Optional[str] = None,
    system: Optional[str] = None,
    process_as_group: bool = False,
    batch_size: int = 20
) -> VideoAnalysisResult:
    try:
        metadata = get_video_metadata(video_path)
        frames = extract_frames(video_path, frame_interval, num_workers)
        params = FrameAnalysisParams(frames, persona, output, stream, batch_size, prompt, system, process_as_group)
        frame_results = await process_video_frames(params)
        return VideoAnalysisResult(metadata, frame_results)
    except Exception as e:
        raise VideoProcessingError(f"Error analyzing video: {str(e)}")

def generate_prompt(persona: Optional[str] = None) -> str:
    base_prompt = "Analyze this video frame and provide a detailed description."
    return f"As a {persona}, {base_prompt}" if persona else base_prompt

def generate_frame_prompt(params: FrameAnalysisParams, start_index: int, batch_size: int) -> str:
    if params.process_as_group:
        frame_numbers = [params.frames[i]['frame_number'] for i in range(start_index, start_index + batch_size)]
        return f"Analyze frames {frame_numbers[0]} to {frame_numbers[-1]} of the video as a group. {params.prompt or generate_prompt(params.persona)}"
    else:
        return f"Analyze frame {params.frames[start_index]['frame_number']} of the video. {params.prompt or generate_prompt(params.persona)}"

def create_frame_result(frame: Dict[str, Any], result: Any) -> Dict[str, Any]:
    return {
        "frame_number": frame['frame_number'],
        "timestamp": frame['timestamp'],
        "result": result
    }
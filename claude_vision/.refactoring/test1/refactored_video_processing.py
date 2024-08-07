from typing import List, Dict, Any, Optional, Tuple
import asyncio
from concurrent.futures import ThreadPoolExecutor
from enum import Enum

from .claude_integration import claude_vision_analysis
from .video_utils import get_video_metadata, extract_frames
from .image_processing import process_multiple_images
from .exceptions import VideoProcessingError

class OutputType(Enum):
    TEXT = "text"
    JSON = "json"
    MARKDOWN = "markdown"

class VideoFrame:
    def __init__(self, frame: Any, frame_number: int, timestamp: float):
        self.frame = frame
        self.frame_number = frame_number
        self.timestamp = timestamp

class VideoAnalysisResult:
    def __init__(self, frame_number: int, timestamp: float, result: Any):
        self.frame_number = frame_number
        self.timestamp = timestamp
        self.result = result

async def process_video_frames(
    frames: List[VideoFrame],
    persona: Optional[str],
    output: OutputType,
    stream: bool,
    batch_size: int = 20,
    prompt: Optional[str] = None,
    system: Optional[str] = None,
    process_as_group: bool = False
) -> List[VideoAnalysisResult]:
    try:
        base64_frames = await process_multiple_images([frame.frame for frame in frames])
        
        async def process_frame_batch(batch_frames: List[str], start_index: int) -> List[VideoAnalysisResult]:
            batch_results = []
            if process_as_group:
                frame_numbers = [frames[i].frame_number for i in range(start_index, start_index + len(batch_frames))]
                frame_prompt = f"Analyze frames {frame_numbers[0]} to {frame_numbers[-1]} of the video as a group. {prompt or generate_prompt(persona)}"
                result = await claude_vision_analysis(batch_frames, frame_prompt, output, stream, system=system)
                for i in range(start_index, start_index + len(batch_frames)):
                    batch_results.append(VideoAnalysisResult(frames[i].frame_number, frames[i].timestamp, result))
            else:
                for i, frame in enumerate(batch_frames, start=start_index):
                    frame_prompt = f"Analyze frame {frames[i].frame_number} of the video. {prompt or generate_prompt(persona)}"
                    result = await claude_vision_analysis([frame], frame_prompt, output, stream, system=system)
                    batch_results.append(VideoAnalysisResult(frames[i].frame_number, frames[i].timestamp, result))
            return batch_results

        with ThreadPoolExecutor() as executor:
            tasks = []
            for i in range(0, len(base64_frames), batch_size):
                batch_frames = base64_frames[i:i+batch_size]
                task = asyncio.create_task(process_frame_batch(batch_frames, i))
                tasks.append(task)
            
            batched_results = await asyncio.gather(*tasks)
            return [result for batch in batched_results for result in batch]
    except Exception as e:
        raise VideoProcessingError(f"Error processing video frames: {str(e)}")

async def analyze_video(
    video_path: str,
    frame_interval: int,
    persona: Optional[str],
    output: OutputType,
    stream: bool,
    num_workers: Optional[int] = None,
    prompt: Optional[str] = None,
    system: Optional[str] = None,
    process_as_group: bool = False
) -> Tuple[Dict[str, Any], List[VideoAnalysisResult]]:
    try:
        metadata = get_video_metadata(video_path)
        frames = [VideoFrame(frame, frame_number, timestamp) for frame, frame_number, timestamp in extract_frames(video_path, frame_interval, num_workers)]
        frame_results = await process_video_frames(frames, persona, output, stream, prompt=prompt, system=system, process_as_group=process_as_group)
        return metadata, frame_results
    except Exception as e:
        raise VideoProcessingError(f"Error analyzing video: {str(e)}")

def generate_prompt(persona: Optional[str] = None) -> str:
    base_prompt = "Analyze this video frame and provide a detailed description."
    return f"As a {persona}, {base_prompt}" if persona else base_prompt
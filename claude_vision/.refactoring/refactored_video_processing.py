from typing import List, Dict, Any, Optional
import asyncio
from concurrent.futures import ThreadPoolExecutor

from .claude_integration import claude_vision_analysis
from .video_utils import get_video_metadata, extract_frames
from .image_processing import process_multiple_images

async def process_video_frames(
    frames: List[Dict[str, Any]],
    persona: Optional[str],
    output: str,
    stream: bool,
    batch_size: int = 20,
    prompt: Optional[str] = None,
    system: Optional[str] = None,
    process_as_group: bool = False
) -> List[Dict[str, Any]]:
    results = []
    base64_frames = await process_multiple_images([frame['frame'] for frame in frames])
    
    async def process_frame_batch(batch_frames: List[str], start_index: int) -> List[Dict[str, Any]]:
        batch_results = []
        frame_prompt = generate_frame_prompt(frames, start_index, len(batch_frames), prompt, persona, process_as_group)
        
        if process_as_group:
            result = await claude_vision_analysis(batch_frames, frame_prompt, output, stream, system=system)
            batch_results = [
                create_frame_result(frames[i], result)
                for i in range(start_index, start_index + len(batch_frames))
            ]
        else:
            for i, frame in enumerate(batch_frames, start=start_index):
                result = await claude_vision_analysis([frame], frame_prompt, output, stream, system=system)
                batch_results.append(create_frame_result(frames[i], result))
        
        return batch_results

    async with ThreadPoolExecutor() as executor:
        tasks = [
            asyncio.create_task(process_frame_batch(base64_frames[i:i+batch_size], i))
            for i in range(0, len(base64_frames), batch_size)
        ]
        
        batched_results = await asyncio.gather(*tasks)
        results = [result for batch in batched_results for result in batch]
    
    return results

async def analyze_video(
    video_path: str,
    frame_interval: int,
    persona: Optional[str],
    output: str,
    stream: bool,
    num_workers: Optional[int] = None,
    prompt: Optional[str] = None,
    system: Optional[str] = None,
    process_as_group: bool = False
) -> Dict[str, Any]:
    metadata = get_video_metadata(video_path)
    frames = extract_frames(video_path, frame_interval, num_workers)
    frame_results = await process_video_frames(
        frames, persona, output, stream,
        prompt=prompt, system=system, process_as_group=process_as_group
    )
    return {"metadata": metadata, "frame_results": frame_results}

def generate_prompt(persona: Optional[str] = None) -> str:
    base_prompt = "Analyze this video frame and provide a detailed description."
    return f"As a {persona}, {base_prompt}" if persona else base_prompt

def generate_frame_prompt(
    frames: List[Dict[str, Any]],
    start_index: int,
    batch_size: int,
    prompt: Optional[str],
    persona: Optional[str],
    process_as_group: bool
) -> str:
    if process_as_group:
        frame_numbers = [frames[i]['frame_number'] for i in range(start_index, start_index + batch_size)]
        return f"Analyze frames {frame_numbers[0]} to {frame_numbers[-1]} of the video as a group. {prompt or generate_prompt(persona)}"
    else:
        return f"Analyze frame {frames[start_index]['frame_number']} of the video. {prompt or generate_prompt(persona)}"

def create_frame_result(frame: Dict[str, Any], result: Any) -> Dict[str, Any]:
    return {
        "frame_number": frame['frame_number'],
        "timestamp": frame['timestamp'],
        "result": result
    }
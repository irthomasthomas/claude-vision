from .claude_integration import claude_vision_analysis
from .video_utils import get_video_metadata, extract_frames
from .image_processing import process_multiple_images
import asyncio
from concurrent.futures import ThreadPoolExecutor

async def process_video_frames(frames, persona, output, stream):
    results = []
    base64_frames = await process_multiple_images([frame['frame'] for frame in frames])
    
    async def process_single_frame(i, frame):
        prompt = f"Analyze frame {frames[i]['frame_number']} of the video. {generate_prompt(persona)}"
        result = await claude_vision_analysis([frame], prompt, output, stream)
        return {
            "frame_number": frames[i]['frame_number'],
            "timestamp": frames[i]['timestamp'],
            "result": result
        }
    
    # Use ThreadPoolExecutor to parallelize API calls
    with ThreadPoolExecutor() as executor:
        tasks = [asyncio.create_task(process_single_frame(i, frame)) for i, frame in enumerate(base64_frames)]
        results = await asyncio.gather(*tasks)
    
    return results

async def analyze_video(video_path, frame_interval, persona, output, stream):
    metadata = get_video_metadata(video_path)
    frames = extract_frames(video_path, frame_interval)
    frame_results = await process_video_frames(frames, persona, output, stream)
    return metadata, frame_results

def generate_prompt(persona=None):
    base_prompt = "Analyze this video frame and provide a detailed description."
    if persona:
        return f"As a {persona}, {base_prompt}"
    return base_prompt
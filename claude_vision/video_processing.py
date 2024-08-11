# video_processing.py - auto_refactory branch
from .claude_integration import claude_vision_analysis
from .video_utils import get_video_metadata, extract_frames
from .image_processing import process_multiple_images
import asyncio
from concurrent.futures import ThreadPoolExecutor

# Todo: I want the option to analyze frames independently or as part of a set of max 20 images.
    #   So that I can analyze differences between frames if need be.
    # This should support --prompt and --system so that I can ask questions about video or use guided generation.
    
async def process_video_frames(frames, persona, output, stream, batch_size=20, prompt=None, system=None, process_as_group=False):
    results = []
    base64_frames = await process_multiple_images([frame['frame'] for frame in frames])
    
    async def process_frame_batch(batch_frames, start_index):
        batch_results = []
        if process_as_group:
            frame_numbers = [frames[i]['frame_number'] for i in range(start_index, start_index + len(batch_frames))]
            frame_prompt = f"Analyze frames {frame_numbers[0]} to {frame_numbers[-1]} of the video as a group. {prompt or generate_prompt(persona)}"
            result = await claude_vision_analysis(batch_frames, frame_prompt, output, stream, system_prompt=system)
            for i in range(start_index, start_index + len(batch_frames)):
                batch_results.append({
                    "frame_number": frames[i]['frame_number'],
                    "timestamp": frames[i]['timestamp'],
                    "result": result
                })
        else:
            for i, frame in enumerate(batch_frames, start=start_index):
                frame_prompt = f"Analyze frame {frames[i]['frame_number']} of the video. {prompt or generate_prompt(persona)}"
                result = await claude_vision_analysis([frame], frame_prompt, output, stream, system_prompt=system)
                batch_results.append({
                    "frame_number": frames[i]['frame_number'],
                    "timestamp": frames[i]['timestamp'],
                    "result": result
                })
        return batch_results

    with ThreadPoolExecutor() as executor:
        tasks = []
        for i in range(0, len(base64_frames), batch_size):
            batch_frames = base64_frames[i:i+batch_size]
            task = asyncio.create_task(process_frame_batch(batch_frames, i))
            tasks.append(task)
        
        batched_results = await asyncio.gather(*tasks)
        for batch_result in batched_results:
            results.extend(batch_result)
    
    return results


async def analyze_video(video_path, frame_interval, persona, output, stream, num_workers=None, prompt=None, system=None, process_as_group=False):
    metadata = get_video_metadata(video_path)
    frames = extract_frames(video_path, frame_interval, num_workers)
    frame_results = await process_video_frames(frames, persona, output, stream, prompt=prompt, system=system, process_as_group=process_as_group)
    return metadata, frame_results

def generate_prompt(persona=None):
    base_prompt = "Analyze this video frame and provide a detailed description."
    if persona:
        return f"As a {persona}, {base_prompt}"
    return base_prompt
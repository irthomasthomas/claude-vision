import cv2
import os
import numpy as np
from concurrent.futures import ProcessPoolExecutor
import multiprocessing
from typing import List, Dict, Tuple, Any
from dataclasses import dataclass

@dataclass
class VideoMetadata:
    fps: float
    frame_count: int
    duration: float
    width: int
    height: int

@dataclass
class FrameData:
    frame: np.ndarray
    frame_number: int
    timestamp: float

class VideoProcessingError(Exception):
    """Base exception for video processing errors."""
    pass

def is_video_file(file_path: str) -> bool:
    """Check if the given file path is a video file."""
    video_extensions = {'.mp4', '.avi', '.mov', '.mkv'}
    return os.path.splitext(file_path)[1].lower() in video_extensions

def get_video_metadata(file_path: str) -> VideoMetadata:
    """Extract metadata from a video file."""
    cap = cv2.VideoCapture(file_path)
    if not cap.isOpened():
        raise VideoProcessingError(f"Failed to open video file: {file_path}")
    
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = frame_count / fps
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    cap.release()
    
    return VideoMetadata(fps, frame_count, duration, width, height)

def process_frame(args: Tuple[np.ndarray, int, float]) -> FrameData:
    """Process a single video frame."""
    frame, frame_number, interval = args
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    return FrameData(frame_rgb, frame_number, frame_number * interval)

def extract_frames(video_path: str, interval: int, num_workers: int = None) -> List[FrameData]:
    """Extract frames from a video file at specified intervals."""
    if num_workers is None:
        num_workers = multiprocessing.cpu_count()

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise VideoProcessingError(f"Failed to open video file: {video_path}")

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_indices = range(0, total_frames, interval)
    
    frames = []
    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        futures = []
        for i in frame_indices:
            cap.set(cv2.CAP_PROP_POS_FRAMES, i)
            ret, frame = cap.read()
            if ret:
                futures.append(executor.submit(process_frame, (frame, i, interval / fps)))
        
        for future in futures:
            frames.append(future.result())
    
    cap.release()
    return frames

def save_frames(frames: List[FrameData], output_dir: str) -> None:
    """Save processed frames as image files."""
    os.makedirs(output_dir, exist_ok=True)
    for frame_data in frames:
        output_path = os.path.join(output_dir, f'frame_{frame_data.frame_number:04d}.jpg')
        cv2.imwrite(output_path, cv2.cvtColor(frame_data.frame, cv2.COLOR_RGB2BGR))

def initialize_gpu() -> None:
    """Initialize GPU for OpenCV if available."""
    if cv2.cuda.getCudaEnabledDeviceCount() > 0:
        cv2.cuda.setDevice(0)

# Initialize GPU at module import
initialize_gpu()
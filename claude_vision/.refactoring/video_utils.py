import cv2
import os
import numpy as np
from concurrent.futures import ProcessPoolExecutor
import multiprocessing
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass

VIDEO_EXTENSIONS = ['.mp4', '.avi', '.mov', '.mkv']

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

def is_video_file(file_path: str) -> bool:
    return os.path.splitext(file_path)[1].lower() in VIDEO_EXTENSIONS

def get_video_metadata(file_path: str) -> VideoMetadata:
    with cv2.VideoCapture(file_path) as cap:
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = frame_count / fps
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    return VideoMetadata(fps, frame_count, duration, width, height)

def process_frame(frame: np.ndarray, frame_number: int, interval: float) -> FrameData:
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    return FrameData(frame_rgb, frame_number, frame_number * interval)

def extract_frames(video_path: str, interval: int, num_workers: Optional[int] = None) -> List[FrameData]:
    num_workers = num_workers or multiprocessing.cpu_count()

    with cv2.VideoCapture(video_path) as cap:
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_indices = range(0, total_frames, interval)
        
        frames = []
        with ProcessPoolExecutor(max_workers=num_workers) as executor:
            futures = [executor.submit(read_and_process_frame, cap, i, interval / fps) for i in frame_indices]
            frames = [future.result() for future in futures if future.result() is not None]
    
    return frames

def read_and_process_frame(cap: cv2.VideoCapture, frame_number: int, interval: float) -> Optional[FrameData]:
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
    ret, frame = cap.read()
    if ret:
        return process_frame(frame, frame_number, interval)
    return None

def save_frames(frames: List[FrameData], output_dir: str) -> None:
    os.makedirs(output_dir, exist_ok=True)
    for frame_data in frames:
        output_path = os.path.join(output_dir, f'frame_{frame_data.frame_number:04d}.jpg')
        cv2.imwrite(output_path, cv2.cvtColor(frame_data.frame, cv2.COLOR_RGB2BGR))

def initialize_gpu() -> None:
    if cv2.cuda.getCudaEnabledDeviceCount() > 0:
        cv2.cuda.setDevice(0)

if __name__ == "__main__":
    initialize_gpu()
    # Add any test or example code here
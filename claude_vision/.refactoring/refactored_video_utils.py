import cv2
import os
import numpy as np
from concurrent.futures import ProcessPoolExecutor
import multiprocessing
from typing import List, Dict, Tuple, Optional

VIDEO_EXTENSIONS = ['.mp4', '.avi', '.mov', '.mkv']

def is_video_file(file_path: str) -> bool:
    return os.path.splitext(file_path)[1].lower() in VIDEO_EXTENSIONS

def get_video_metadata(file_path: str) -> Dict[str, float]:
    with cv2.VideoCapture(file_path) as cap:
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = frame_count / fps
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    return {
        'fps': fps,
        'frame_count': frame_count,
        'duration': duration,
        'width': width,
        'height': height
    }

def process_frame(frame: np.ndarray, frame_number: int, interval: float) -> Dict[str, any]:
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    return {
        'frame': frame_rgb,
        'frame_number': frame_number,
        'timestamp': frame_number * interval
    }
    
def extract_frames(video_path: str, interval: int, num_workers: Optional[int] = None) -> List[Dict[str, any]]:
    num_workers = num_workers or multiprocessing.cpu_count()

    with cv2.VideoCapture(video_path) as cap:
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
                    futures.append(executor.submit(process_frame, frame, i, interval / fps))
            
            for future in futures:
                frames.append(future.result())
    
    return frames

def save_frames(frames: List[Dict[str, any]], output_dir: str) -> None:
    os.makedirs(output_dir, exist_ok=True)
    for frame_data in frames:
        frame = frame_data['frame']
        frame_number = frame_data['frame_number']
        output_path = os.path.join(output_dir, f'frame_{frame_number:04d}.jpg')
        cv2.imwrite(output_path, cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))

def initialize_gpu() -> None:
    if cv2.cuda.getCudaEnabledDeviceCount() > 0:
        cv2.cuda.setDevice(0)

if __name__ == "__main__":
    initialize_gpu()
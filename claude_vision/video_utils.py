# video_utils.py - auto_refactory branch

import cv2
import os
import numpy as np
from concurrent.futures import ProcessPoolExecutor
import multiprocessing

def is_video_file(file_path):
    video_extensions = ['.mp4', '.avi', '.mov', '.mkv']
    _, ext = os.path.splitext(file_path)
    return ext.lower() in video_extensions

def get_video_metadata(file_path):
    cap = cv2.VideoCapture(file_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = frame_count / fps
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    cap.release()
    return {
        'fps': fps,
        'frame_count': frame_count,
        'duration': duration,
        'width': width,
        'height': height
    }

def process_frame(args):
    frame, frame_number, interval = args
    # Convert BGR to RGB
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    return {
        'frame': frame_rgb,
        'frame_number': frame_number,
        'timestamp': frame_number * interval
    }
    
def extract_frames(video_path, interval, num_workers=None):
    if num_workers is None:
        num_workers = multiprocessing.cpu_count()

    cap = cv2.VideoCapture(video_path)
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

def save_frames(frames, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    for frame_data in frames:
        frame = frame_data['frame']
        frame_number = frame_data['frame_number']
        cv2.imwrite(os.path.join(output_dir, f'frame_{frame_number:04d}.jpg'), frame)

# Check if CUDA is available and set OpenCV to use GPU
if cv2.cuda.getCudaEnabledDeviceCount() > 0:
    cv2.cuda.setDevice(0)
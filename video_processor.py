import asyncio
import os
from typing import List, Callable
import ffmpeg

class VideoProcessor:
    async def analyze_video(self, video_path: str) -> dict:
        probe = await asyncio.to_thread(ffmpeg.probe, video_path)
        video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
        
        return {
            "filename": os.path.basename(video_path),
            "size": f"{os.path.getsize(video_path) / (1024 * 1024):.2f} MB",
            "duration": f"{float(video_stream['duration']):.2f} seconds",
            "format": video_stream['codec_name']
        }

    async def generate_screenshots(self, video_path: str, num_screenshots: int, progress_callback: Callable[[float], None]) -> List[str]:
        probe = await asyncio.to_thread(ffmpeg.probe, video_path)
        duration = float(probe['streams'][0]['duration'])
        
        screenshots = []
        for i in range(num_screenshots):
            timestamp = 1 if i == 0 else i * (duration / (num_screenshots - 1))
            output_path = f"screenshot_{i+1}.jpg"
            
            await asyncio.to_thread(
                ffmpeg.input(video_path, ss=timestamp)
                .filter('scale', 1280, -1)
                .output(output_path, vframes=1)
                .overwrite_output()
                .run, capture_stdout=True, capture_stderr=True
            )
            
            screenshots.append(output_path)
            progress_callback((i + 1) / num_screenshots)

        return screenshots

    def cleanup(self, video_path: str):
        if os.path.exists(video_path):
            os.remove(video_path)
        
        for file in os.listdir():
            if file.startswith("screenshot_") and file.endswith(".jpg"):
                os.remove(file)

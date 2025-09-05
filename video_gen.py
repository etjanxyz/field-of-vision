import os
import logging
import requests
import time
import base64
from dotenv import load_dotenv

logger = logging.getLogger(__name__)
load_dotenv()

class VideoGenerator:
    def __init__(self):
        self.api_key = os.getenv("RUNWAY_API_SECRET")  # Updated to match Runway's expected env var
        self.base_url = "https://api.dev.runwayml.com/v1"
        self.save_dir = os.getenv("SAVE_DIRECTORY", "./generated_videos")
        
        # Create save directory if it doesn't exist
        os.makedirs(self.save_dir, exist_ok=True)
        
        if not self.api_key:
            logger.warning("RUNWAY_API_SECRET not found in environment variables")

    def generate(self, image_path, image_prompt=None):
        """
        Generate video from image using Runway Gen-2 API
        Falls back to simple pan/zoom effect if API fails
        """
        try:
            video_path = self._generate_runway(image_path, image_prompt)
            if not video_path:
                video_path = self._generate_fallback(image_path)
            return video_path
        except Exception as e:
            logger.error(f"Error generating video: {str(e)}")
            return None

    def _generate_runway(self, image_path, image_prompt=None):
        """Generate video using Runway Gen-3 API"""
        try:
            if not self.api_key:
                logger.error("Runway API key not configured")
                return None

            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # Convert image to base64
            with open(image_path, 'rb') as f:
                image_data = base64.b64encode(f.read()).decode('utf-8')
            
            # Generate video prompt based on image prompt
            video_prompt = self._create_video_prompt(image_prompt)
            
            # Create video generation task
            payload = {
                "model": "gen4",
                "prompt": video_prompt,
                "promptImage": f"data:image/jpeg;base64,{image_data}",
                "duration": 5,
                "ratio": "16:9",
                "watermark": False
            }
            
            logger.info(f"Creating video generation task with prompt: {video_prompt}")
            
            # Submit generation request
            response = requests.post(
                f"{self.base_url}/image_to_video",
                headers=headers,
                json=payload
            )
            
            if response.status_code != 200:
                logger.error(f"Failed to create video generation task: {response.status_code} - {response.text}")
                return None
            
            task_data = response.json()
            task_id = task_data.get("id")
            
            if not task_id:
                logger.error("No task ID returned from Runway API")
                return None
            
            logger.info(f"Video generation task created with ID: {task_id}")
            
            # Poll for completion
            video_url = self._poll_for_completion(task_id, headers)
            if not video_url:
                return None
            
            # Download and save video
            return self._download_video(video_url)
            
        except Exception as e:
            logger.error(f"Error with Runway API: {str(e)}")
            return None

    def _poll_for_completion(self, task_id, headers, max_wait_time=300):
        """Poll the task status until completion"""
        start_time = time.time()
        
        while time.time() - start_time < max_wait_time:
            try:
                response = requests.get(
                    f"{self.base_url}/tasks/{task_id}",
                    headers=headers
                )
                
                if response.status_code != 200:
                    logger.error(f"Failed to get task status: {response.status_code}")
                    return None
                
                task_data = response.json()
                status = task_data.get("status")
                
                logger.info(f"Task {task_id} status: {status}")
                
                if status == "SUCCEEDED":
                    output = task_data.get("output")
                    if output and len(output) > 0:
                        return output[0]  # Return the video URL
                    else:
                        logger.error("No output found in completed task")
                        return None
                
                elif status == "FAILED":
                    failure_reason = task_data.get("failure")
                    logger.error(f"Task failed: {failure_reason}")
                    return None
                
                elif status in ["PENDING", "RUNNING"]:
                    # Task is still processing, wait and check again
                    time.sleep(10)
                    continue
                
                else:
                    logger.warning(f"Unknown task status: {status}")
                    time.sleep(10)
                    continue
                    
            except Exception as e:
                logger.error(f"Error polling task status: {str(e)}")
                time.sleep(10)
                continue
        
        logger.error(f"Task {task_id} did not complete within {max_wait_time} seconds")
        return None

    def _download_video(self, video_url):
        """Download video from URL and save to local file"""
        try:
            logger.info(f"Downloading video from: {video_url}")
            
            response = requests.get(video_url, stream=True)
            if response.status_code != 200:
                logger.error(f"Failed to download video: {response.status_code}")
                return None
            
            # Generate unique filename
            timestamp = int(time.time())
            save_path = os.path.join(self.save_dir, f"runway_video_{timestamp}.mp4")
            
            # Save video file
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            logger.info(f"Video saved to: {save_path}")
            return save_path
            
        except Exception as e:
            logger.error(f"Error downloading video: {str(e)}")
            return None

    def _create_video_prompt(self, image_prompt):
        """
        Generate a video prompt based on the image generation prompt
        """
        if not image_prompt:
            return "Subtle ambient motion"
        
        # Extract key elements from the image prompt
        prompt_lower = image_prompt.lower()
        
        # Define motion keywords based on scene elements
        motion_mappings = {
            'peaceful': 'gentle swaying, soft movement',
            'dramatic': 'dynamic motion, cinematic movement',
            'landscape': 'slow camera pan, natural movement',
            'forest': 'leaves rustling, gentle wind',
            'ocean': 'waves flowing, water movement',
            'mountain': 'clouds drifting, atmospheric movement',
            'sunset': 'light shifting, golden hour movement',
            'storm': 'dramatic clouds, intense movement',
            'field': 'grass swaying, wind movement',
            'river': 'water flowing, ripples',
            'desert': 'sand shifting, heat shimmer',
            'snow': 'snowflakes falling, winter ambiance',
            'rain': 'raindrops falling, atmospheric',
            'fog': 'mist rolling, ethereal movement',
            'fire': 'flames dancing, warm glow',
            'stars': 'twinkling, celestial movement'
        }
        
        # Find matching motion elements
        motion_elements = []
        for keyword, motion in motion_mappings.items():
            if keyword in prompt_lower:
                motion_elements.append(motion)
        
        # Create video prompt
        if motion_elements:
            video_prompt = f"Cinematic {', '.join(motion_elements[:2])}, smooth camera movement, atmospheric"
        else:
            video_prompt = "Subtle ambient motion, cinematic atmosphere, gentle movement"
        
        logger.info(f"Generated video prompt: {video_prompt}")
        return video_prompt

    def _generate_fallback(self, image_path):
        """
        Generate a simple pan and zoom effect video using OpenCV
        This is used as a fallback when the API fails
        """
        try:
            import cv2
            import numpy as np
            
            # Read image
            img = cv2.imread(image_path)
            height, width = img.shape[:2]
            
            # Create video writer
            save_path = os.path.join(self.save_dir, f"generated_{len(os.listdir(self.save_dir))}.mp4")
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(save_path, fourcc, 30.0, (width, height))
            
            # Generate simple ken burns effect
            zoom_factor = 1.0
            for i in range(150):  # 5 seconds at 30fps
                zoom_factor += 0.001
                M = cv2.getRotationMatrix2D((width/2, height/2), 0, zoom_factor)
                frame = cv2.warpAffine(img, M, (width, height))
                out.write(frame)
                
            out.release()
            return save_path
            
        except Exception as e:
            logger.error(f"Error generating fallback video: {str(e)}")
            return None

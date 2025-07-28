import os
import logging
import requests
from dotenv import load_dotenv

logger = logging.getLogger(__name__)
load_dotenv()

class VideoGenerator:
    def __init__(self):
        self.api_key = os.getenv("VIDEO_GEN_API_KEY")
        self.save_dir = os.getenv("SAVE_DIRECTORY", "./generated_videos")
        
        # Create save directory if it doesn't exist
        os.makedirs(self.save_dir, exist_ok=True)

    def generate(self, image_path):
        """
        Generate video from image using Runway Gen-2 API
        Falls back to simple pan/zoom effect if API fails
        """
        try:
            video_path = self._generate_runway(image_path)
            if not video_path:
                video_path = self._generate_fallback(image_path)
            return video_path
        except Exception as e:
            logger.error(f"Error generating video: {str(e)}")
            return None

    def _generate_runway(self, image_path):
        """Generate video using Runway Gen-2 API"""
        try:
            # This is a placeholder for the Runway API implementation
            # You'll need to implement the actual API calls based on Runway's documentation
            
            # Example structure:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # Upload image
            with open(image_path, 'rb') as f:
                files = {'image': f}
                response = requests.post(
                    "https://api.runwayml.com/v1/uploads",
                    headers=headers,
                    files=files
                )
                
            # Generate video
            video_response = requests.post(
                "https://api.runwayml.com/v1/generate",
                headers=headers,
                json={
                    "prompt": "Subtle ambient motion",
                    "image": response.json()["id"],
                    "duration": 5
                }
            )
            
            # Download video
            video_url = video_response.json()["video_url"]
            video_content = requests.get(video_url).content
            
            # Save video
            save_path = os.path.join(self.save_dir, f"generated_{len(os.listdir(self.save_dir))}.mp4")
            with open(save_path, 'wb') as f:
                f.write(video_content)
                
            return save_path
            
        except Exception as e:
            logger.error(f"Error with Runway API: {str(e)}")
            return None

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

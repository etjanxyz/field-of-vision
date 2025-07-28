import os
import logging
import requests
from PIL import Image
from io import BytesIO
import torch
from diffusers import StableDiffusionPipeline
from dotenv import load_dotenv

logger = logging.getLogger(__name__)
load_dotenv()

class ImageGenerator:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.save_dir = os.getenv("SAVE_DIRECTORY", "./generated_images")
        
        # Create save directory if it doesn't exist
        os.makedirs(self.save_dir, exist_ok=True)
        
        # Initialize Stable Diffusion if GPU is available
        if torch.cuda.is_available():
            try:
                self.sd_pipeline = StableDiffusionPipeline.from_pretrained(
                    "CompVis/stable-diffusion-v1-4",
                    torch_dtype=torch.float16
                )
                self.sd_pipeline = self.sd_pipeline.to("cuda")
                self.use_local = True
                logger.info("Using local Stable Diffusion model")
            except Exception as e:
                logger.warning(f"Could not load local Stable Diffusion: {str(e)}")
                self.use_local = False
        else:
            self.use_local = False
            logger.info("No GPU available, using DALL-E API")

    def generate(self, prompt):
        """Generate image from prompt using either local SD or DALL-E API"""
        try:
            if self.use_local:
                return self._generate_local(prompt)
            else:
                return self._generate_dalle(prompt)
        except Exception as e:
            logger.error(f"Error generating image: {str(e)}")
            return None

    def _generate_local(self, prompt):
        """Generate image using local Stable Diffusion"""
        try:
            # Generate image
            image = self.sd_pipeline(
                prompt,
                num_inference_steps=50,
                guidance_scale=7.5
            ).images[0]
            
            # Save image
            save_path = os.path.join(self.save_dir, f"generated_{len(os.listdir(self.save_dir))}.png")
            image.save(save_path)
            
            return save_path
            
        except Exception as e:
            logger.error(f"Error with local generation: {str(e)}")
            return None

    def _generate_dalle(self, prompt):
        """Generate image using DALL-E API"""
        try:
            response = requests.post(
                "https://api.openai.com/v1/images/generations",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "prompt": prompt,
                    "n": 1,
                    "size": "1024x1024"
                }
            )
            
            response.raise_for_status()
            image_url = response.json()["data"][0]["url"]
            
            # Download image
            image_response = requests.get(image_url)
            image = Image.open(BytesIO(image_response.content))
            
            # Save image
            save_path = os.path.join(self.save_dir, f"generated_{len(os.listdir(self.save_dir))}.png")
            image.save(save_path)
            
            return save_path
            
        except Exception as e:
            logger.error(f"Error with DALL-E API: {str(e)}")
            return None

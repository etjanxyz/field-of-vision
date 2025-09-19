import os
import logging
import requests
from PIL import Image
from io import BytesIO
from dotenv import load_dotenv

logger = logging.getLogger(__name__)
load_dotenv()

class ImageGenerator:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.save_dir = os.getenv("SAVE_DIRECTORY", "./generated_images")
        os.makedirs(self.save_dir, exist_ok=True)

    def _enhance_prompt(self, prompt):
        """Transform literal descriptions into more atmospheric ones"""
        # Convert literal descriptions to atmospheric ones
        prompt = prompt.lower()
        
        atmospheric_mappings = {
            "wall of trees": "dense forest canopy",
            "sunlight shining through": "ethereal sunbeams filtering through the trees",
            "light through": "golden light streaming through",
            "wall of": "dense, majestic",
            "shining": "radiating",
            "beam": "ray of light",
            "beams": "rays of light"
        }
        
        # Apply mappings
        enhanced = prompt
        for literal, atmospheric in atmospheric_mappings.items():
            enhanced = enhanced.replace(literal, atmospheric)
        
        # Add artistic and atmospheric qualities, explicitly prevent UI/text
        enhanced = (
            f"{enhanced}, pure photographic scene, no text, no UI elements, no overlays, "
            "no watermarks, no icons, no interface elements, clean natural image, "
            "cinematic photography, masterful composition, professional landscape photography, "
            "artful lighting, breathtaking natural beauty, moody atmosphere, "
            "purely photorealistic, no graphical elements"
        )
        
        return enhanced

    def generate(self, prompt):
        """Generate image using DALL-E API"""
        try:
            print("Generating image with DALL-E...")
            
            # Transform prompt to be more atmospheric and explicitly prevent UI/text
            enhanced_prompt = self._enhance_prompt(prompt)
            print(f"Enhanced prompt: {enhanced_prompt}")
            
            response = requests.post(
                "https://api.openai.com/v1/images/generations",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "prompt": enhanced_prompt,
                    "n": 1,
                    "size": "1024x1024",
                    "model": "dall-e-3",
                    "quality": "hd",
                    "style": "natural",  # Ensure natural photographic style
                }
            )
            
            response.raise_for_status()
            image_url = response.json()["data"][0]["url"]
            print("Image generated, downloading...")
            
            # Download image
            image_response = requests.get(image_url)
            image = Image.open(BytesIO(image_response.content))
            
            # Save image
            save_path = os.path.join(self.save_dir, f"generated_{len(os.listdir(self.save_dir))}.png")
            image.save(save_path)
            print(f"Image saved: {save_path}")
            
            return save_path
            
        except Exception as e:
            logger.error(f"Error with DALL-E API: {str(e)}")
            return None

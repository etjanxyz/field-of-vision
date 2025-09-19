import os
import time
import json
import base64
import logging
import random
import requests
from dotenv import load_dotenv

logger = logging.getLogger(__name__)
load_dotenv()

RUNWAY_API = "https://api.dev.runwayml.com/v1"
RUNWAY_VERSION = "2024-11-06"

class VideoGenerator:
    def __init__(self):
        self.api_key = os.getenv("RUNWAY_API_SECRET")
        if not self.api_key:
            logger.error("No RUNWAY_API_SECRET found in environment variables")
        self.save_dir = os.getenv("SAVE_DIRECTORY", "./generated_videos")
        
        # Motion mappings focused on internal motion only
        self.motion_mappings = {
            # Light Effects
            'sunlight': [
                'Completely static frame. Internal motion only: light beams gently shifting intensity, dust particles floating in light shafts, subtle air currents affecting light patterns',
                'Fixed camera. Light dynamics: ethereal rays slowly intensifying and fading, floating particles catching light, gentle atmospheric movement',
                'Locked frame. Light animation: beams of light gradually shifting, airborne particles drifting through light, delicate atmospheric effects'
            ],
            'forest': [
                'Perfectly still camera. Internal forest motion: leaves gently swaying, light filtering through canopy, subtle shadow play on ground',
                'Fixed position. Forest dynamics: foliage movement in light breeze, dappled light patterns shifting, gentle understory motion',
                'Static frame. Woodland motion: branches swaying softly, light and shadow interplay, forest floor detail movement'
            ],
            'trees': [
                'Absolutely fixed camera. Tree motion: leaves rustling in breeze, shifting light through branches, natural canopy movement',
                'Locked position. Arboreal motion: foliage swaying gently, light patterns through leaves, branch and leaf interaction',
                'Static shot. Tree dynamics: leaf movement in wind, light filtering effects, natural forest motion'
            ],
            'light': [
                'Completely static view. Light effects: rays shifting intensity, atmospheric particles in beams, gentle light evolution',
                'Fixed frame. Lighting dynamics: beam intensity variation, floating particles in light, subtle atmospheric movement',
                'Locked camera. Light animation: soft ray movement, airborne particle effects, delicate light changes'
            ],
            
            # Default nature motion
            'default': [
                'Absolutely static camera. Natural motion: subtle environmental movement, gentle atmospheric effects, soft light variation',
                'Fixed frame. Environmental dynamics: delicate element motion, atmospheric flow, light interplay',
                'Locked position. Scene motion: soft natural movement, light and shadow play, gentle atmospheric drift'
            ]
        }
        
        os.makedirs(self.save_dir, exist_ok=True)

    def _get_motion_prompt(self, scene_description: str) -> str:
        """
        Generate motion prompt with absolutely static camera
        """
        scene_description = scene_description.lower()
        
        # Start with absolute camera lock statement
        motion_elements = [
            "Camera is completely locked and static - absolutely no camera movement, panning, or drift whatsoever. "
            "All motion is purely environmental and internal to the scene. "
        ]
        
        # Find matching environmental effects
        matched_effects = []
        for keyword, prompts in self.motion_mappings.items():
            if keyword in scene_description:
                matched_effects.append(random.choice(prompts))
        
        # If no specific effects found, use default nature motion
        if not matched_effects:
            matched_effects = [random.choice(self.motion_mappings['default'])]
        
        motion_elements.extend(matched_effects)
        
        # Emphasize static camera again in final prompt
        prompt = (
            f"{' '.join(motion_elements)} "
            "Remember: Camera must remain completely static - no movement whatsoever. "
            "Focus entirely on internal scene motion while maintaining photorealistic quality."
        )
        
        logger.info(f"Generated motion prompt: {prompt}")
        return prompt

    def generate(self, image_path, scene_description):
        """Generate video from image using Runway API"""
        try:
            if not self.api_key:
                logger.error("Cannot generate video: No Runway API key configured")
                return None
                
            return self._generate_runway(image_path, scene_description)
        except Exception as e:
            logger.exception(f"Error generating video: {e}")
            return None

    def _headers(self):
        """Get headers for Runway API requests"""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "X-Runway-Version": RUNWAY_VERSION,
        }

    def _generate_runway(self, image_path, scene_description):
        """Generate video using Runway API with static camera"""
        try:
            # Build motion prompt
            prompt_text = self._get_motion_prompt(scene_description)

            # Encode image
            with open(image_path, "rb") as f:
                b64 = base64.b64encode(f.read()).decode("utf-8")
            data_uri = f"data:image/png;base64,{b64}"

            # Create task
            payload = {
                "model": "gen3a_turbo",
                "promptImage": data_uri,
                "promptText": prompt_text,
                "duration": 5,
                "ratio": "1280:768"
            }

            logger.info("Submitting image_to_video task to Runway...")
            r = requests.post(
                f"{RUNWAY_API}/image_to_video",
                headers=self._headers(),
                json=payload,
                timeout=60
            )
            
            if r.status_code != 200:
                logger.error(f"Runway create failed [{r.status_code}]: {r.text}")
                return None

            task_id = r.json().get("id")
            if not task_id:
                logger.error(f"No task id in response: {r.text}")
                return None

            # Poll for completion
            logger.info(f"Task created: {task_id}. Polling for completion...")
            backoff = 1.0
            for _ in range(120):  # ~2 minutes max
                tr = requests.get(
                    f"{RUNWAY_API}/tasks/{task_id}",
                    headers=self._headers(),
                    timeout=30
                )
                
                if tr.status_code != 200:
                    logger.warning(f"Task poll failed [{tr.status_code}]: {tr.text}")
                else:
                    td = tr.json()
                    status = td.get("status")
                    
                    if status == "SUCCEEDED":
                        outputs = td.get("output") or []
                        if not outputs:
                            logger.error(f"Task succeeded but no outputs: {json.dumps(td)[:500]}")
                            return None
                            
                        video_url = outputs[0]
                        logger.info(f"Downloading video: {video_url}")
                        vr = requests.get(video_url, timeout=120)
                        
                        if vr.status_code != 200:
                            logger.error(f"Video download failed [{vr.status_code}]")
                            return None
                            
                        save_path = os.path.join(self.save_dir, f"generated_{len(os.listdir(self.save_dir))}.mp4")
                        with open(save_path, "wb") as f:
                            f.write(vr.content)
                            
                        logger.info("Successfully generated video.")
                        return save_path
                        
                    elif status in {"FAILED", "CANCELED", "CANCELLED"}:
                        logger.error(f"Runway task ended with status: {status}")
                        return None
                    
                time.sleep(backoff)
                backoff = min(backoff * 1.5, 5.0)

            logger.error("Timed out waiting for Runway task to finish.")
            return None
            
        except Exception as e:
            logger.error(f"Error with Runway API: {str(e)}")
            logger.exception("Full traceback:")
            return None

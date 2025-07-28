#!/usr/bin/env python3
import json
import os
from dotenv import load_dotenv
import logging
from queue_manager import QueueManager
from audio_listener import AudioListener
from transcriber import Transcriber
from prompt_parser import PromptParser
from image_gen import ImageGenerator
from video_gen import VideoGenerator
from video_player import VideoPlayer

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class FieldOfVision:
    def __init__(self):
        # Load environment variables and configuration
        load_dotenv()
        with open('config.json', 'r') as f:
            self.config = json.load(f)

        # Initialize components
        self.queue_manager = QueueManager(self.config)
        self.audio_listener = AudioListener(self.config)
        self.transcriber = Transcriber()
        self.prompt_parser = PromptParser()
        self.image_generator = ImageGenerator()
        self.video_generator = VideoGenerator()
        self.video_player = VideoPlayer(self.config)

    def start(self):
        """Main execution loop"""
        logger.info("Starting Field of Vision...")
        
        try:
            # Start video player in a separate thread
            self.video_player.start()

            while True:
                # Record audio
                audio_data = self.audio_listener.record()
                
                # Transcribe speech to text
                text = self.transcriber.transcribe(audio_data)
                if not text:
                    continue

                # Parse text to generate image prompt
                prompt = self.prompt_parser.parse(text)
                if not prompt:
                    continue

                # Generate image
                image_path = self.image_generator.generate(prompt)
                if not image_path:
                    continue

                # Generate video
                video_path = self.video_generator.generate(image_path)
                if not video_path:
                    continue

                # Add to queue
                self.queue_manager.add_video(video_path)

        except KeyboardInterrupt:
            logger.info("Shutting down...")
            self.cleanup()

    def cleanup(self):
        """Cleanup resources"""
        self.video_player.stop()
        # Add any other cleanup needed

if __name__ == "__main__":
    app = FieldOfVision()
    app.start()

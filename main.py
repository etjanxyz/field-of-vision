#!/usr/bin/env python3
import json
import os
from dotenv import load_dotenv
import logging
import warnings
from queue_manager import QueueManager
from audio_listener import AudioListener
from transcriber import Transcriber
from prompt_parser import PromptParser
from image_gen import ImageGenerator
from video_gen import VideoGenerator
from video_player import VideoPlayer

# Suppress all warnings
warnings.filterwarnings('ignore')

# Minimal logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)
logger = logging.getLogger(__name__)

class FieldOfVision:
    def __init__(self):
        print("\nInitializing Field of Vision...")
        
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
        print("\nField of Vision ready - Speak your scene description (Press Ctrl+C to exit)")
        
        try:
            # Start video player in a separate thread
            self.video_player.start()

            while True:
                print("\nListening for audio...")
                audio_data = self.audio_listener.record()
                
                if not audio_data:
                    print("No audio detected, trying again...")
                    continue

                print("Transcribing audio...")
                text = self.transcriber.transcribe(audio_data)
                if not text:
                    print("Could not transcribe audio, please try again...")
                    continue

                print(f"\nTranscribed: {text}")

                prompt = self.prompt_parser.parse(text)
                if not prompt:
                    print("Could not generate prompt, please try again...")
                    continue

                image_path = self.image_generator.generate(prompt)
                if not image_path:
                    print("Could not generate image, please try again...")
                    continue

                print("\nGenerating video animation...")
                video_path = self.video_generator.generate(image_path, prompt)
                if not video_path:
                    print("Could not generate video, please try again...")
                    continue

                print("\nVideo generated successfully!")
                self.queue_manager.add_video(video_path)

        except KeyboardInterrupt:
            print("\nShutting down...")
            self.cleanup()

    def cleanup(self):
        """Cleanup resources"""
        self.video_player.stop()

if __name__ == "__main__":
    os.environ['PYTHONWARNINGS'] = 'ignore'
    app = FieldOfVision()
    app.start()

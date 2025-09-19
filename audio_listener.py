import sounddevice as sd
import numpy as np
import wave
import os
import logging
import time
import sys

logger = logging.getLogger(__name__)

class AudioListener:
    def __init__(self, config):
        self.device_index = config.get('audio_device_index', 0)
        self.sample_rate = config.get('sample_rate', 44100)
        self.channels = config.get('channels', 1)
        self.chunk_size = config.get('chunk_size', 1024)
        self.record_seconds = config.get('record_seconds', 10)  # Increased to 10 seconds

    def record(self):
        """Record audio from microphone with countdown"""
        logger.info("Recording audio...")
        print("\nRecording starts in:")
        for i in range(3, 0, -1):
            print(f"{i}...")
            time.sleep(0.5)
        
        print(f"\nRecording... ({self.record_seconds} seconds)")
        print("Speak your description (time remaining: ", end='', flush=True)
        
        try:
            # Calculate total frames
            frames = int(self.sample_rate * self.record_seconds)
            
            # Start recording
            recording = sd.rec(
                frames,
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype=np.int16
            )
            
            # Show countdown while recording
            for remaining in range(self.record_seconds, 0, -1):
                sys.stdout.write(f"\rSpeak your description (time remaining: {remaining}s)")
                sys.stdout.flush()
                time.sleep(1)
            
            print("\nProcessing...")
            
            # Wait for recording to finish
            sd.wait()
            
            # Save recording temporarily
            temp_file = "temp_recording.wav"
            with wave.open(temp_file, 'wb') as wf:
                wf.setnchannels(self.channels)
                wf.setsampwidth(2)  # 2 bytes for int16
                wf.setframerate(self.sample_rate)
                wf.writeframes(recording.tobytes())
            
            logger.info("Audio recording completed")
            return temp_file
            
        except Exception as e:
            logger.error(f"Error recording audio: {str(e)}")
            return None

    def list_devices(self):
        """List available audio devices"""
        return sd.query_devices()

    def test_audio(self):
        """Test audio recording"""
        print("Recording test audio...")
        recording = self.record()
        if recording:
            print("Recording successful!")
            return True
        return False

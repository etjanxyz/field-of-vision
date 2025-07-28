import sounddevice as sd
import numpy as np
import wave
import os
import logging

logger = logging.getLogger(__name__)

class AudioListener:
    def __init__(self, config):
        self.device_index = config.get('audio_device_index', 0)
        self.sample_rate = config.get('sample_rate', 44100)
        self.channels = config.get('channels', 1)
        self.chunk_size = config.get('chunk_size', 1024)
        self.record_seconds = config.get('record_seconds', 5)

    def record(self):
        """Record audio from microphone"""
        logger.info("Recording audio...")
        
        try:
            # Calculate total frames
            frames = int(self.sample_rate * self.record_seconds)
            
            # Record audio
            recording = sd.rec(
                frames,
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype=np.int16
            )
            
            # Wait until recording is finished
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

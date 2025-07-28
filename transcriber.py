import whisper
import logging
import os

logger = logging.getLogger(__name__)

class Transcriber:
    def __init__(self):
        self.model = whisper.load_model("base")
        
    def transcribe(self, audio_file):
        """
        Transcribe audio file to text using Whisper
        """
        try:
            if not os.path.exists(audio_file):
                logger.error(f"Audio file not found: {audio_file}")
                return None
                
            # Transcribe audio
            result = self.model.transcribe(audio_file)
            transcribed_text = result["text"].strip()
            
            # Clean up temporary audio file
            try:
                os.remove(audio_file)
            except Exception as e:
                logger.warning(f"Could not remove temporary audio file: {str(e)}")
            
            logger.info(f"Transcribed text: {transcribed_text}")
            return transcribed_text
            
        except Exception as e:
            logger.error(f"Error transcribing audio: {str(e)}")
            return None

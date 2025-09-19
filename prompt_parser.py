import logging

logger = logging.getLogger(__name__)

class PromptParser:
    def __init__(self):
        pass

    def parse(self, text):
        """
        Parse transcribed text to extract relevant landscape description
        and enhance it for image generation
        """
        try:
            if not text:
                return None
                
            # Simple enhancement of the input text
            prompt = f"A cinematic landscape scene of {text}, photorealistic style, professional photography"
            print(f"Enhanced prompt: {prompt}")
            return prompt
                
        except Exception as e:
            logger.error(f"Error parsing text: {str(e)}")
            return None

    def clean_text(self, text):
        """Remove unnecessary words and normalize text"""
        return text.strip().lower()

import spacy
import logging
from transformers import pipeline

logger = logging.getLogger(__name__)

class PromptParser:
    def __init__(self):
        # Load spaCy model for NLP processing
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            logger.info("Downloading spaCy model...")
            spacy.cli.download("en_core_web_sm")
            self.nlp = spacy.load("en_core_web_sm")
            
        # Load sentiment analyzer
        self.sentiment_analyzer = pipeline("sentiment-analysis")

    def parse(self, text):
        """
        Parse transcribed text to extract relevant landscape description
        and enhance it for image generation
        """
        try:
            if not text:
                return None
                
            # Process text with spaCy
            doc = self.nlp(text.lower())
            
            # Extract relevant parts (nouns, adjectives, etc.)
            landscape_elements = []
            for token in doc:
                if token.pos_ in ["NOUN", "ADJ"] and not token.is_stop:
                    landscape_elements.append(token.text)
                    
            # Get sentiment to influence style
            sentiment = self.sentiment_analyzer(text)[0]
            mood = "peaceful" if sentiment["label"] == "POSITIVE" else "dramatic"
            
            # Construct enhanced prompt
            if landscape_elements:
                prompt = f"A {mood} landscape with {', '.join(landscape_elements)}, cinematic lighting, detailed, atmospheric"
                logger.info(f"Generated prompt: {prompt}")
                return prompt
            else:
                logger.warning("No relevant landscape elements found in text")
                return None
                
        except Exception as e:
            logger.error(f"Error parsing text: {str(e)}")
            return None

    def clean_text(self, text):
        """Remove unnecessary words and normalize text"""
        # Add any specific text cleaning rules here
        return text.strip().lower()

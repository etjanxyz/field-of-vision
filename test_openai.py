import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API key from environment variable
api_key = os.getenv('OPENAI_API_KEY')

def test_chat():
    print("Testing Chat API...")
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": "Create a short description of a peaceful landscape"}]
    }
    response = requests.post(url, headers=headers, json=data)
    print(json.dumps(response.json(), indent=2))

def test_image():
    print("\nTesting Image Generation API...")
    url = "https://api.openai.com/v1/images/generations"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    data = {
        "model": "dall-e-3",
        "prompt": "A serene mountain landscape at sunset",
        "n": 1,
        "size": "1024x1024"
    }
    response = requests.post(url, headers=headers, json=data)
    print(json.dumps(response.json(), indent=2))

if __name__ == "__main__":
    test_chat()
    test_image()

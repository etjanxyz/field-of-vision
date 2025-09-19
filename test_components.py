import os
import urllib.request
import json
import ssl
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API key from environment variable
api_key = os.getenv('OPENAI_API_KEY')

def make_request(url, data):
    context = ssl._create_unverified_context()
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode('utf-8'),
        headers=headers,
        method='POST'
    )
    
    try:
        with urllib.request.urlopen(req, context=context) as response:
            return json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        print(f"Error: {e.code}")
        print(e.read().decode('utf-8'))
        return None

def test_chat():
    print("Testing Chat API...")
    url = "https://api.openai.com/v1/chat/completions"
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": "Create a short description of a peaceful landscape"}]
    }
    response = make_request(url, data)
    if response:
        print(json.dumps(response, indent=2))

def test_image():
    print("\nTesting Image Generation API...")
    url = "https://api.openai.com/v1/images/generations"
    data = {
        "model": "dall-e-3",
        "prompt": "A serene mountain landscape at sunset",
        "n": 1,
        "size": "1024x1024"
    }
    response = make_request(url, data)
    if response:
        print(json.dumps(response, indent=2))

if __name__ == "__main__":
    print("Testing Field of Vision components...")
    test_chat()
    test_image()

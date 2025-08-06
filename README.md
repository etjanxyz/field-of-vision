<b>🌀 AI-Powered Landscape Experience: Field of Vision README</b>
<br>
This guide walks you through setting up an interactive, generative art system in which visitor speech drives the creation of dynamic AI landscapes that evolve into ambient moving visuals. The full experience culminates in a continuously playing, immersive projection.
<p></p>
<b>🎯 System Overview</b>
<br>
Visitor OnboardingVisitors hear onboarding instructions that explain how to “speak to the AI” to create images.
Speech to Prompt ParsingVisitors speak into a microphone. Speech is transcribed to text, and key promptable language (e.g., “misty mountains at dusk”) is extracted using NLP parsing.
<br>
Image GenerationThe parsed prompt is fed into an AI image generator (e.g., DALL·E, Stable Diffusion) to produce a landscape image.
Video SynthesisThe static image is sent to a video-generation API (e.g., RunwayML Gen-2, Pika, or Kaiber) to create a short, animated ambient loop.
Local Storage & QueuingThe resulting video is saved locally and added to a video player’s playlist queue.
Full-Screen PlaybackThe video player runs in fullscreen mode, looping through ambient videos. When needed, it can randomly re-loop previous videos while new ones generate.
Projection/DisplayOutput is mirrored or projected for immersive installation viewing.
<p></p>
<b>🧰 Requirements</b>
<br>
Software
Speech-to-Text API (e.g., Google Speech, Whisper)
NLP Parser for extracting promptable content (e.g., spaCy, GPT)
Image Generation Model (e.g., Stable Diffusion, DALL·E)
Video Generation API (e.g., RunwayML Gen-2, Pika Labs)
Video Queueing Player (custom script with VLC or Python-based player)
Queue Manager / Local File Tracker
Hardware
Microphone input
Local computer (see hardware section below)
Secondary display / projector
GPU acceleration (for local inference, optional but recommended)
Sufficient local storage (for saved videos)
<p></p>
<b>🔧 Installation & Setup</b>
<br>
1. Onboarding Audio
Record or synthesize a voice prompt explaining how to speak to the AI (e.g., “Say something like ‘a moonlit desert at night’…”).
Loop this audio until user input is detected.
2. Audio Capture & Transcription
Use a microphone to record user speech.
Process audio through speech-to-text service (e.g., Whisper API).
Store the transcription for NLP analysis.
3. Prompt Parsing
Run transcription through a keyword extractor or GPT-based classifier.
Output a clean prompt for an image generation model.
4. Image Generation
Use prompt to generate landscape via Stable Diffusion or other image models.
Save image temporarily to disk or RAM.
5. Video Generation
Pass image into a video-generation API.
Receive a short (~5–10s) loopable ambient video.
Store video to local disk.
6. Queue Management
Add new video to local playlist JSON or queue system.
If video gen is slow, allow playback of random previous entries.
7. Playback & Projection
Run a fullscreen media player in loop mode.
Optionally use Python with OpenCV/Pygame, or a script that manages VLC or MPV.
Mirror or route to projector/screen.
<p></p>
<b>♻️ Runtime Architecture</b>
<br>
flowchart LR    A[Visitor speaks] --> B[Speech-to-text]    B --> C[NLP Prompt Extractor]    C --> D[AI Image Generation]    D --> E[Video Synthesis API]    E --> F[Save Video Locally]    F --> G[Add to Video Queue]    G --> H[Video Player (Fullscreen)]    H --> I[Projection Output]
<p></p>
<b>📂 Configuration Templates</b>
<br>
.env (Environment Variables)
WHISPER_API_KEY=your_whisper_key
OPENAI_API_KEY=your_openai_key
VIDEO_GEN_API_KEY=your_video_gen_key
SAVE_DIRECTORY=./generated_videos
PROJECTOR_DISPLAY=:1
config.json (Queue Manager Settings)
{
  "video_queue_file": "playlist.json",
  "fallback_videos": ["fallback1.mp4", "fallback2.mp4"],
  "video_loop_duration": 10,
  "retry_interval": 5
}
<p></p>
<b>🛋️ Packaging for Deployment</b>
<br>
Dockerfile (For MCP Controller)
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
CMD ["python", "main.py"]
requirements.txt
openai
whisper
opencv-python
pygame
python-vlc
requests
run.sh (Launch Script)
#!/bin/bash
export $(grep -v '^#' .env | xargs)
python main.py
<p></p>
<b>🔧 Suggested Scripts</b>
<br>
main.py: Orchestrates entire pipeline
audio_listener.py: Captures mic input and saves audio
transcriber.py: Sends audio to Whisper
prompt_parser.py: Extracts visual language
image_gen.py: Calls Stable Diffusion or DALL·E
video_gen.py: Sends image to video-generation API
queue_manager.py: Adds file to JSON queue
video_player.py: Plays videos from playlist in fullscreen loop

<p></p>
<b>🥪 Development Tips</b>
<br>
Test each pipeline module independently before integration.
Pre-load a few ambient videos for fallback.
Cache recent prompts to avoid repeat generations.
Consider using SSD storage for faster video read/write.
<p></p>
<b>🚀 Future Enhancements</b>
<br>
Allow visitor to choose between themes (e.g., “dreamy,” “chaotic”).
Add ambient audio generation to match visuals.
Enable multi-user queuing with RFID or NFC tags.
Local-only (offline) version using entirely open-source models.

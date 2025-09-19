import vlc
import pygame
import logging
import threading
import time
import os

logger = logging.getLogger(__name__)

class VideoPlayer:
    def __init__(self, config):
        self.config = config
        self.running = False
        self.current_video = None
        self.display_output = config.get('display_output', ':1')
        
        # Initialize either VLC or Pygame
        try:
            self.player = self._init_vlc()
            self.using_vlc = True
            logger.info("Using VLC for video playback")
        except Exception as e:
            logger.warning(f"Failed to initialize VLC: {str(e)}")
            self.player = self._init_pygame()
            self.using_vlc = False
            logger.info("Using Pygame for video playback")

    def _init_vlc(self):
        """Initialize VLC player"""
        instance = vlc.Instance()
        player = instance.media_player_new()
        
        # Set fullscreen
        player.set_fullscreen(True)
        
        # Set output display if specified
        if self.display_output:
            player.set_xwindow(int(self.display_output.replace(':', '')))
            
        return player

    def _init_pygame(self):
        """Initialize Pygame player as fallback"""
        pygame.init()
        pygame.display.init()
        
        # Set display if specified
        if self.display_output:
            os.environ['SDL_VIDEODRIVER'] = 'x11'
            os.environ['DISPLAY'] = self.display_output
            
        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        return screen

    def start(self):
        """Start video playback in a separate thread"""
        self.running = True
        self.thread = threading.Thread(target=self._playback_loop)
        self.thread.daemon = True
        self.thread.start()

    def stop(self):
        """Stop video playback"""
        self.running = False
        if self.thread:
            self.thread.join()
        self._cleanup()

    def _playback_loop(self):
        """Main playback loop"""
        while self.running:
            try:
                if self.using_vlc:
                    self._vlc_playback()
                else:
                    self._pygame_playback()
            except Exception as e:
                logger.error(f"Playback error: {str(e)}")
                time.sleep(1)

    def _vlc_playback(self):
        """Handle VLC playback"""
        if self.current_video and os.path.exists(self.current_video):
            media = self.player.get_instance().media_new(self.current_video)
            self.player.set_media(media)
            self.player.play()
            
            # Wait for video to finish
            time.sleep(1)  # Give time for video to start
            while self.running and self.player.is_playing():
                time.sleep(0.1)

    def _pygame_playback(self):
        """Handle Pygame playback (fallback)"""
        if self.current_video and os.path.exists(self.current_video):
            try:
                # This is a simplified version - in reality you'd need
                # to properly decode and play video frames
                pass
            except Exception as e:
                logger.error(f"Pygame playback error: {str(e)}")

    def set_video(self, video_path):
        """Set the current video to play"""
        self.current_video = video_path

    def _cleanup(self):
        """Clean up resources"""
        if self.using_vlc:
            self.player.stop()
            self.player.release()
        else:
            pygame.quit()

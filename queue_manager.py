import json
import os
import logging
from threading import Lock

logger = logging.getLogger(__name__)

class QueueManager:
    def __init__(self, config):
        self.queue_file = config['video_queue_file']
        self.fallback_videos = config['fallback_videos']
        self.lock = Lock()
        
        # Initialize queue file if it doesn't exist
        if not os.path.exists(self.queue_file):
            self._save_queue([])

    def add_video(self, video_path):
        """Add a new video to the queue"""
        try:
            with self.lock:
                queue = self._load_queue()
                queue.append(video_path)
                self._save_queue(queue)
                logger.info(f"Added video to queue: {video_path}")
                return True
        except Exception as e:
            logger.error(f"Error adding video to queue: {str(e)}")
            return False

    def get_next_video(self):
        """Get the next video from the queue"""
        try:
            with self.lock:
                queue = self._load_queue()
                if not queue:
                    # Return a fallback video if queue is empty
                    return self._get_fallback_video()
                    
                # Get next video and verify it exists
                video_path = queue[0]
                if not os.path.exists(video_path):
                    logger.warning(f"Video file not found: {video_path}")
                    queue.pop(0)  # Remove missing video
                    self._save_queue(queue)
                    return self._get_fallback_video()
                    
                return video_path
                
        except Exception as e:
            logger.error(f"Error getting next video: {str(e)}")
            return self._get_fallback_video()

    def remove_video(self, video_path):
        """Remove a video from the queue"""
        try:
            with self.lock:
                queue = self._load_queue()
                if video_path in queue:
                    queue.remove(video_path)
                    self._save_queue(queue)
                    logger.info(f"Removed video from queue: {video_path}")
                return True
        except Exception as e:
            logger.error(f"Error removing video from queue: {str(e)}")
            return False

    def _load_queue(self):
        """Load the queue from file"""
        try:
            with open(self.queue_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading queue: {str(e)}")
            return []

    def _save_queue(self, queue):
        """Save the queue to file"""
        try:
            with open(self.queue_file, 'w') as f:
                json.dump(queue, f)
        except Exception as e:
            logger.error(f"Error saving queue: {str(e)}")

    def _get_fallback_video(self):
        """Return a fallback video path"""
        for video in self.fallback_videos:
            if os.path.exists(video):
                return video
        logger.error("No fallback videos available")
        return None

    def get_queue_length(self):
        """Get the current length of the queue"""
        try:
            with self.lock:
                return len(self._load_queue())
        except Exception as e:
            logger.error(f"Error getting queue length: {str(e)}")
            return 0

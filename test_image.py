import os
import time
import random
from instagrapi import Client
from dotenv import load_dotenv
import logging
import tempfile
import requests


# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class InstagramTester:
    def __init__(self):
        self.client = Client()
        self._setup_device()
        self.username = os.getenv("INSTAGRAM_USERNAME")
        self.password = os.getenv("INSTAGRAM_PASSWORD")
        self.session_file = "instagram_session.json"
        
    def _setup_device(self):
        """Mimic a real Android device"""
        self.client.set_user_agent("Instagram 289.0.0.30.120 Android (25/7.1.2; 380dpi; 1080x1920; unknown/Android; realme RMX1993; RMX1993; qcom; en_US; 367216753)")
        self.client.set_device({
            "manufacturer": "realme",
            "model": "RMX1993",
            "android_version": 25,
            "android_release": "7.1.2"
        })
        
    def _human_delay(self, min_sec=1, max_sec=3):
        """Random wait between actions"""
        time.sleep(random.uniform(min_sec, max_sec))
        
    def login(self):
        """Smart login with session reuse"""
        try:
            if os.path.exists(self.session_file):
                self.client.load_settings(self.session_file)
                if self.client.user_id:
                    logger.info("Reused existing session")
                    return True
                    
            self._human_delay()
            login_result = self.client.login(self.username, self.password)
            
            if not login_result:
                logger.error("Login failed")
                return False
                
            self.client.dump_settings(self.session_file)
            logger.info("New login successful")
            return True
            
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            return False
            
    def post_content(self, image_url: str, caption: str):
        """Safe post with human-like patterns"""
        try:
            # Download image
            img_path = self._download_image(image_url)
            
            # Add emoji variation
            caption = self._enhance_caption(caption)
            
            # Simulate human editing time
            self._human_delay(2, 5)
            
            # Upload post
            self.client.photo_upload(
                path=img_path,
                caption=caption,
                extra_data={"disable_comments": False}
            )
            
            # Random post-activity
            if random.random() > 0.7:
                self.client.user_stories(random.randint(1, 3))
                
            return True
            
        except Exception as e:
            logger.error(f"Post failed: {str(e)}")
            return False
            
    def _download_image(self, url: str) -> str:
        """Save image to temp file"""
        response = requests.get(url)
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
        temp_file.write(response.content)
        temp_file.close()
        return temp_file.name
        
    def _enhance_caption(self, caption: str) -> str:
        """Add random emoji variations"""
        emojis = ["🔥", "🌟", "💪", "✨", "🚀"]
        return f"{random.choice(emojis)} {caption} {random.choice(emojis)}"

if __name__ == "__main__":
    # Example usage
    tester = InstagramTester()
    
    if tester.login():
        test_post = tester.post_content(
            image_url="https://picsum.photos/1080/1080",  # Random test image
            caption="Test post from automated system 🤖"
        )
        
        if test_post:
            logger.info("Posted successfully! Check your Instagram account.")
        else:
            logger.error("Posting failed")
    else:
        logger.error("Cannot proceed without login")
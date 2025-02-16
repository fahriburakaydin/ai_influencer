import requests
from config import Config
from logger import logger
from instagrapi import Client  # Import instagrapi
from getpass import getpass # To get the code without showing it in the console

import os
from instagrapi.exceptions import  ChallengeRequired, LoginRequired
import tempfile
from getpass import getpass # To get the code without showing it in the console
from flask import session
import time
import random
from dotenv import load_dotenv

import os
import time
import random
from instagrapi import Client

import logging

load_dotenv()


class InstagramPoster:  #not used atm
    def __init__(self):
        self.base_url = "https://graph.facebook.com/v19.0"
        self.access_token = Config.INSTAGRAM_ACCESS_TOKEN
        self.ig_user_id = Config.INSTAGRAM_ACCOUNT_ID

    def post_to_instagram(self, image_url: str, caption: str) -> bool:
        """Publish post to Instagram using Facebook Graph API"""
        try:
            # Step 1: Upload image
            image_id = self._upload_image(image_url)
            
            # Step 2: Create container
            container_id = self._create_container(image_id, caption)
            
            # Step 3: Publish
            return self._publish_post(container_id)
            
        except Exception as e:
            logger.error(f"Instagram posting failed: {str(e)}")
            return False

    def _upload_image(self, image_url: str) -> str:
        """Upload image to Instagram's server"""
        url = f"{self.base_url}/{self.ig_user_id}/media"
        params = {
            "image_url": image_url,
            "access_token": self.access_token
        }
        
        response = requests.post(url, params=params)
        response.raise_for_status()
        return response.json()['id']

    def _create_container(self, image_id: str, caption: str) -> str:
        """Create post container"""
        url = f"{self.base_url}/{self.ig_user_id}/media_publish"
        params = {
            "creation_id": image_id,
            "caption": caption,
            "access_token": self.access_token
        }
        
        response = requests.post(url, params=params)
        response.raise_for_status()
        return response.json()['id']

    def _publish_post(self, container_id: str) -> bool:
        """Confirm publication"""
        url = f"{self.base_url}/{container_id}"
        params = {"fields": "status_code", "access_token": self.access_token}
        
        response = requests.get(url, params=params)
        return response.json()['status_code'] == "FINISHED"
    
        
class InstagrApiPoster:
    def __init__(self):
        self.client = Client()
        self._setup_device()
        self.session_file = "instagram_session.json"
        
    def _setup_device(self):
        self.client.set_user_agent("Instagram 289.0.0.30.120 Android (25/7.1.2; 380dpi; 1080x1920; unknown/Android; realme RMX1993; RMX1993; qcom; en_US; 367216753)")
        self.client.set_device({
            "manufacturer": "realme",
            "model": "RMX1993",
            "android_version": 25,
            "android_release": "7.1.2"
        })
        
    def _human_delay(self, min_delay=1, max_delay=3):  # Updated to accept parameters
        """Human-like delay with configurable range"""
        time.sleep(random.uniform(min_delay, max_delay))
        
    def login(self, code=None):
        try:
            if os.path.exists(self.session_file):
                try:
                    self.client.load_settings(self.session_file)
                    # Changed from get_user_id() to check authentication properly
                    if self.client.user_id:
                        logger.info("Reused existing session")
                        return True
                except Exception as e:
                    logger.warning(f"Session load failed: {str(e)}")

            self._human_delay()
            
            if code:
                # Handle 2FA code submission
                challenge = self.client.challenge_resolve(self.client.last_login_params)
                self.client.challenge_code(code.strip(), challenge)
                if self.client.user_id:
                    self.client.dump_settings(self.session_file)
                    return True
                return False
            
            # Normal login
            login_result = self.client.login(
                Config.INSTAGRAM_USERNAME,
                Config.INSTAGRAM_PASSWORD
            )
            
            if login_result:
                self.client.dump_settings(self.session_file)
                logger.info("New login successful")
                return True
            return False
            
        except ChallengeRequired as e:
            logger.warning("2FA challenge required")
            self.client.dump_settings(self.session_file)
            raise
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            return False

    def post_content(self, image_url: str, caption: str) -> bool:
        """Safe post with human-like patterns"""
        try:
            if Config.TEST_MODE:
                logger.info("TEST_MODE: Skipping Instagram post")
                return True

            # Enhanced caption
            caption = self._enhance_caption(caption)
            
            # Download image with random delay
            self._human_delay()
            image_path = self._download_image(image_url)

            # Simulate human editing time
            self._human_delay(2, 5)

            # Upload post
            self.client.photo_upload(
                path=image_path,
                caption=caption,
                extra_data={
                    "disable_comments": False,
                    "like_and_view_counts_disabled": False
                }
            )

            # Random post-activity simulation
            if random.random() > 0.7:
                self._simulate_organic_activity()

            return True

        except Exception as e:
            logger.error(f"Post failed: {str(e)}")
            return False
        finally:
            if os.path.exists(image_path):
                os.remove(image_path)

    def _enhance_caption(self, caption: str) -> str:
        """Add natural-looking variations to captions"""
        emojis = ["🔥", "🌟", "💡", "✨", "🚀", "💎", "👑"]
        return f"{random.choice(emojis)} {caption} {random.choice(emojis)}"

    def _simulate_organic_activity(self):
        """Random account interactions"""
        actions = [
            lambda: self.client.user_following(self.client.user_id, amount=1),
            lambda: self.client.user_likers(self.client.user_id, amount=1),
            lambda: self.client.user_stories(self.client.user_id, amount=1)
        ]
        random.choice(actions)()
        self._human_delay(3, 7)

    def _download_image(self, url: str) -> str:
        """Download image with randomized headers"""
        headers = {
            "User-Agent": random.choice([
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15"
            ])
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
        temp_file.write(response.content)
        temp_file.close()
        return temp_file.name
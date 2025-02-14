import requests
from config import Config
from logger import logger
from instagrapi import Client  # Import instagrapi
from getpass import getpass # To get the code without showing it in the console

import os
from instagrapi.exceptions import  ChallengeRequired
import tempfile
from getpass import getpass # To get the code without showing it in the console
from flask import session



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
    

class InstagrApiPoster: # New class (instagrapi)
    def __init__(self):
        self.username = Config.INSTAGRAM_USERNAME
        self.password = Config.INSTAGRAM_PASSWORD
        self.client = Client()  # Initialize the instagrapi client
        #self._configure_proxy() 
        self.client.request_timeout = 15  # seconds
        self.client.max_retries = 2
        self.client.delay_range = [5, 10]  # Seconds between actions

    def _configure_proxy(self):
        if Config.INSTAGRAM_TEST_PROXY:
            self.client.set_proxy(Config.INSTAGRAM_TEST_PROXY)
            
    def login(self):
        """Handle login with 2FA, asking for the code in the terminal"""
        if session.get('2fa_code'):
            try:
                self.client.challenge_resolve(session.pop('2fa_code'))
                return True
            except Exception as e:
                logger.error(f"2FA failed: {str(e)}")    

        try:
            logger.info("Logging in to Instagram")
            self.client.login(self.username, self.password)
            logger.info("Instagram login successful")
            return True
        except ChallengeRequired:
            try:
                logger.info("2FA required. Please enter the code from your email.")
                code = getpass(prompt="Enter 2FA code: ")
                self.client.challenge_code(code)
                self.client.save_settings("instagram_settings.json")
                logger.info("2FA successful. Session saved.")
                return True
            except Exception as e:
                logger.error(f"2FA authentication failed: {e}")
                return False
        except Exception as e:
            logger.error(f"Instagrapi login failed: {e}")
            return False

    def post_content(self, image_url: str, caption: str) -> bool:
        """Post to Instagram with error handling"""
        if Config.TEST_MODE:
            logger.info("TEST_MODE: Skipping Instagram post")
            return True
            
        try:
            # Download image from Replicate
            image_path = self._download_image(image_url)
            
            # Upload post
            self.client.photo_upload(
                path=image_path,
                caption=caption,
                extra_data={
                    "disable_comments": False,
                    "like_and_view_counts_disabled": False
                }
            )
            logger.info("Posted to Instagram successfully")
            return True
        except Exception as e:
            logger.error(f"Instagram post failed: {str(e)}")
            return False
        finally:
            if os.path.exists(image_path):
                os.remove(image_path)  # Cleanup temp file

    def _download_image(self, url: str) -> str:
        """Download image to temporary file"""
        response = requests.get(url)
        response.raise_for_status()
        
        _, ext = os.path.splitext(url)
        temp_file = tempfile.NamedTemporaryFile(
            suffix=ext or ".jpg",
            delete=False
        )
        temp_file.write(response.content)
        temp_file.close()
        return temp_file.name
import requests
from config import Config
from logger import logger

class InstagramPoster:
    def __init__(self):
        self.base_url = "https://graph.facebook.com/v19.0"
        self.access_token = Config.INSTAGRAM_ACCESS_TOKEN
        self.ig_user_id = Config.INSTAGRAM_ACCOUNT_ID

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

  

    def post_to_instagram(self, image_url: str, caption: str) -> bool:
        """Publish post to Instagram using Facebook Graph API"""
        if Config.TEST_MODE:
            logger.info("TEST_MODE: Would post to Instagram")
        return True
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

    def _publish_post(self, container_id: str) -> bool:
        """Confirm publication"""
        url = f"{self.base_url}/{container_id}"
        params = {"fields": "status_code", "access_token": self.access_token}
        
        response = requests.get(url, params=params)
        return response.json()['status_code'] == "FINISHED"
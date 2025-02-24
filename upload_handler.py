"""
Upload Handler Module

This module handles image uploads. When an image is uploaded,
it generates a visual caption (using the image captioner) and saves the image data,
including the visual caption, into the store_images table.
"""

import os
from database import save_store_image
from agents.image_captioner import generate_visual_caption
from logger import logger

def handle_image_upload(store_id: int, image_path: str, user_description: str = ""):
    """
    Handles the image upload process.
    
    :param store_id: The ID of the store uploading the image.
    :param image_path: The file path of the uploaded image.
    :param user_description: Optional text provided by the user.
    """
    try:
        # Generate the visual caption from the image using the captioner module.
        visual_caption = generate_visual_caption(image_path)
        
        # Save the image information to the database, including the visual caption.
        save_store_image(store_id, image_path, description=user_description, visual_caption=visual_caption)
        logger.info(f"Image uploaded and saved with visual caption: {visual_caption}")
    except Exception as e:
        logger.error(f"Failed to handle image upload for {image_path}: {str(e)}")

# For testing purposes:
if __name__ == "__main__":
    test_store_id = 1
    test_image_path = r"C:\Users\fahri\github\personal\ai_influencer\static\uploads\Milou.jpg"
    test_user_description = ""  # Or provide a description if available.
    
    handle_image_upload(test_store_id, test_image_path, test_user_description)

# agents/caption_generator.py
from openai import OpenAI
from config import Config
from exceptions import APIError
from testing import mock_text_generation, should_mock
from logger import logger

def generate_caption(post_idea: str) -> str:
    """
    Generate Instagram caption for a post idea with error handling and testing support
    """
    logger.info(f"Generating caption for: {post_idea[:50]}...")
    
    if should_mock():
        logger.debug("Using mock caption generation")
        return mock_text_generation(post_idea)
    
    try:
        client = OpenAI(api_key=Config.OPENAI_API_KEY)
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{
                "role": "user",
                "content": f"""
                Create an engaging Instagram caption about: {post_idea}
                Requirements:
                - Include 3-5 relevant hashtags at the end
                - Use emojis where appropriate
                - Keep it under 220 characters
                - Use a friendly, motivational tone
                """
            }]
        )
        
        caption = response.choices[0].message.content.strip()
        
        # Basic validation
        if not caption or len(caption) > 300:
            raise APIError("Caption generation failed validation")
            
        return caption
        
    except Exception as e:
        logger.error(f"Caption generation failed: {str(e)}")
        raise APIError("Failed to generate caption") from e
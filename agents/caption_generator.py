# agents/caption_generator.py
from openai import OpenAI
from config import Config
from exceptions import APIError
from testing import mock_text_generation, should_mock
from logger import logger
import random

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
            model=Config.MODEL,
            messages=[{
                "role": "user",
                "content": f"""
                Create an Instagram caption about: {post_idea}
                
                Requirements:
                - First line: Attention-grabbing hook (include 1 relevant emoji)
                - Second line: Value proposition or interesting fact
                - Third line: Call-to-action or question
                - Hashtags: 3-5 niche-specific hashtags at end
                - Tone: {random.choice(["Funny", "Inspirational", "Curious"])}
                - MAKE SURE THE CAPTION IS LESS THAN 250 CHARACTERS!!
                - Avoid: Generic phrases like "check this out"
                """
            }]
        )
        
        caption = response.choices[0].message.content.strip()
        print(f"generated caption: {caption}")
        
        # Basic validation
        if not caption or len(caption) > 350:
            print(f"Caption is {len(caption)} characters")
            raise APIError("Caption generation failed validation")
            
        return caption
        
    except Exception as e:
        logger.error(f"Caption generation failed: {str(e)}")
        raise APIError("Failed to generate caption") from e
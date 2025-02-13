import replicate
from config import Config
from exceptions import APIError
from testing import mock_image_generation, should_mock
from logger import logger

def generate_image(post_idea: str) -> str:
    try:
        if Config.TEST_MODE:
            return "https://placehold.co/600x400"
            
        # Enhanced prompt template
        prompt = f"""
        Instagram-worthy photo for influencer post about: {post_idea}
        Style: Professional photography, vibrant colors, trending Instagram aesthetic
        Details: Include natural lighting, modern composition, aspirational mood
        """
        
        # Add negative prompts to avoid common issues
        output = replicate.run(
            "stability-ai/sdxl:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b",
            input={
                "prompt": prompt,
                "negative_prompt": "blurry, text, watermark, low quality, cartoon, drawing",
                "num_inference_steps": 40,
                "guidance_scale": 9.5
            }
        )
        
        return str(output[0])
        
    except Exception as e:
        logger.error(f"Image generation failed: {str(e)}")
        raise APIError("Failed to generate image") from e
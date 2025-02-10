import replicate
from config import Config
from exceptions import APIError
from testing import mock_image_generation, should_mock
from logger import logger

def generate_image(prompt: str) -> str:
    try:
        if Config.TEST_MODE:
            logger.debug("Using mock image generation")
            return "https://placehold.co/600x400"  # Mock URL
            
        logger.info(f"Generating image for: {prompt[:50]}...")
        
        output = replicate.run(
            "stability-ai/sdxl:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b",
            input={"prompt": prompt}
        )
        
        # Ensure the output is converted to a string
        return str(output[0])
        
    except Exception as e:
        logger.error(f"Image generation failed: {str(e)}")
        raise APIError("Failed to generate image") from e
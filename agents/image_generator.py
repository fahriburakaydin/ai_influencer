import replicate
from config import Config
from exceptions import APIError
from testing import mock_image_generation, should_mock
from logger import logger

def generate_image(post_idea: str, store_details: dict = None) -> str:
    """
    Generates an AI-generated Instagram-worthy image based on post idea and store branding.

    :param post_idea: The core idea for the Instagram post.
    :param store_details: Optional store-specific information such as brand aesthetics and signature products.
    :return: URL of the generated image.
    """
    try:
        if Config.TEST_MODE:
            return "https://placehold.co/600x400"
        
        #  Extract store-specific details (fallback to defaults if missing)
        store_name = store_details.get("store_name", "a business") if store_details else "a business"
        brand_voice = store_details.get("brand_voice", "modern and vibrant") if store_details else "modern and vibrant"
        signature_products = store_details.get("signature_products", "products") if store_details else "products"

        #  Enhanced AI prompt for personalized branding
        prompt = f"""
        Instagram-worthy photo for {store_name}, showcasing {signature_products}.
        Style: {brand_voice}, professional photography, trending Instagram aesthetic.
        Details: Natural lighting, modern composition, aspirational and visually appealing.
        """
        
        # Add negative prompts to avoid unwanted elements
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

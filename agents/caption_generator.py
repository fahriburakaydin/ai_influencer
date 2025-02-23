# agents/caption_generator.py
from openai import OpenAI
from config import Config
from exceptions import APIError
from testing import mock_text_generation, should_mock
from logger import logger
import random

def generate_caption(post_idea: str, store_details: dict = None) -> str:
    """
    Generate an Instagram caption for a post idea, incorporating store-specific details.

    :param post_idea: The core idea for the Instagram post.
    :param store_details: Optional store-specific information such as brand voice and signature products.
    :return: A store-personalized Instagram caption.
    """
    logger.info(f"Generating caption for: {post_idea[:50]}...")

    if should_mock():
        logger.debug("Using mock caption generation")
        return mock_text_generation(post_idea)
    
    try:
        client = OpenAI(api_key=Config.OPENAI_API_KEY)

        # Extract store-specific details (fallback to defaults if missing)
        store_name = store_details.get("store_name", "our brand") if store_details else "our brand"
        brand_voice = store_details.get("brand_voice", "witty and professional") if store_details else "witty and professional"
        signature_products = store_details.get("signature_products", "exciting products") if store_details else "exciting products"
        fun_facts = store_details.get("fun_facts", "a fun fact") if store_details else "a fun fact"
        store_adress = store_details.get("store_adress", "store adress") if store_details else "store adress"

        response = client.chat.completions.create(
            model=Config.MODEL,
            messages=[{
                "role": "user",
                "content": f"""
                You are an expert Instagram copywriter, crafting engaging captions for {store_name}.
                Your captions should match the store's brand voice: {brand_voice}.

                Create a short, high-impact Instagram caption for: {post_idea}.
                Include also the following store details if relevant:
                - Fun Fact: {fun_facts}
                - Signature Products: {signature_products}
                -store_adress: {store_adress}
                -store_name: {store_name}   

                Requirements:
                - First line: Attention-grabbing hook (include 1 relevant emoji).
                - Second line: Value proposition or interesting fact related to {store_name} or its products.
                - Third line: Call-to-action or question.
                - Hashtags: 3-5 niche-specific hashtags at the end.
                - If relevant, mention {signature_products}.
                - Tone: {random.choice(["Funny", "Inspirational", "Curious"])}.
                - MAKE SURE THE CAPTION IS LESS THAN 250 CHARACTERS!!
                - Avoid: Generic phrases like "check this out".
                - Use an inclusive tone (avoid 'guys', prefer 'everyone' or 'friends').
                """
            }]
        )
        
        caption = response.choices[0].message.content.strip()
        print(f"Generated caption: {caption}")

        # Basic validation
        if not caption or len(caption) > 350:
            print(f"Caption is {len(caption)} characters. Too long!")
            raise APIError("Caption generation failed validation")

        return caption
        
    except Exception as e:
        logger.error(f"Caption generation failed: {str(e)}")
        raise APIError("Failed to generate caption") from e

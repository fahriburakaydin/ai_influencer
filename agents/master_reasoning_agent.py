import openai
import json
from config import Config
from logger import logger

def clean_json_output(raw_text: str) -> str:
    """Remove markdown code blocks and trim whitespace from JSON output."""
    cleaned = raw_text.replace("```json", "").replace("```", "")
    return cleaned.strip()

def master_reasoning_agent(niche: str, research_data: dict, store_details: dict, visual_captions: list) -> list:
    """
    Uses DeepSeek R1 (via its OpenAI-compatible API) to generate:
      - A final narrative summarizing the overall strategy.
      - A tailored image prompt for generating an Instagram-worthy image.
      - A tailored caption prompt for creating a concise Instagram caption.
    
    Returns a list of alternative outputs (each a dict with keys 'final_narrative', 'image_prompt', and 'caption_prompt').
    """
    combined_context = (
        f"Store '{store_details.get('store_name', 'our store')}' has a brand voice of '{store_details.get('brand_voice', 'neutral')}', "
        f"fun facts: '{store_details.get('fun_facts', 'none')}', and signature products: '{store_details.get('signature_products', 'unspecified')}'. "
        f"In the niche '{niche}', current trends include: {', '.join(research_data.get('niche_trends', []))}. "
        f"Recommended content strategies on the internet include: {', '.join(research_data.get('content_strategies', []))}. "
        f"Visual impressions from our images: {', '.join(visual_captions)}."
    )
    
    user_prompt = (
        "Given the following context:\n"
        f"{combined_context}\n\n"
        "Generate exactly TWO ALTERNATIVE OUTPUTS in valid JSON format as an array, where each element is an object with the keys:\n"
         "Your goal is to produce creative social media content that balances the following elements:\n\n"
        "1. **Research Insights**: Leverage the research trends and content strategies to stay current and relevant.\n"
        "2. **Brand Identity**: Use the store's details (brand voice, fun facts) to maintain a consistent tone in the captions. \n"
        "3. **Common Sense & Balance**: Decide which aspects from the research and the brand should be emphasized for the best overall impact.\n\n"
        "3. **Do not use any og the store information while generating the image prompt.\n\n"

        "For each alternative output, include:\n"
        "  'final_narrative': A final narrative summarizing the overall strategy and context.\n"
        "  'image_prompt': A detailed image prompt for generating an Instagram-worthy image that aligns with the context. Do not include any text in the images\n"
        "  'caption_prompt': A concise, engaging Instagram caption (under 250 characters) that complements the image.\n\n"
        "Ensure that your output is complete, well-formed JSON without any markdown formatting. "
        "Every JSON object must be fully closed, and the JSON array must end with a closing square bracket (])."
    )
    
    output_text = ""
    
    try:
        client = openai.OpenAI(
            api_key=Config.DEEPSEEK_API_KEY,
            base_url="https://api.deepseek.com"
        )
        response = client.chat.completions.create(
            model=Config.REASON_MODEL,  # e.g., "deepseek-reasoner"
            messages=[
                {"role": "system", "content": "You are a highly experienced social media strategist."},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=600
        )
        
        output_text = response.choices[0].message.content.strip()
        if not output_text:
            logger.error("DeepSeek API returned an empty output.")
            return [{"final_narrative": "", "image_prompt": "", "caption_prompt": ""}]
        
        # Clean the output to remove markdown formatting
        cleaned_output = clean_json_output(output_text)
        logger.debug(f"Cleaned output: {cleaned_output}")
        
        # Fallback: if the cleaned output does not end with a closing square bracket, append it.
        if not cleaned_output.endswith("]"):
            logger.debug("Cleaned output does not end with ']', appending it.")
            cleaned_output += "]"
        
        try:
            result_array = json.loads(cleaned_output)
            if not isinstance(result_array, list) or len(result_array) < 1:
                logger.error("JSON response is not an array with at least one alternative.")
                return [{"final_narrative": "", "image_prompt": "", "caption_prompt": ""}]
            # Return the full list of alternatives
            return result_array
        except json.JSONDecodeError as jde:
            logger.error(f"JSON decode error: {str(jde)}")
            logger.error(f"Raw output: {output_text}")
            logger.error(f"Cleaned output: {cleaned_output}")
            return [{"final_narrative": "", "image_prompt": "", "caption_prompt": ""}]
    except Exception as e:
        logger.error(f"Error in master reasoning agent using DeepSeek R1: {str(e)}")
        return [{"final_narrative": "", "image_prompt": "", "caption_prompt": ""}]

if __name__ == "__main__":
    # Sample test data for the Master Reasoning Agent.
    niche = "beauty"
    research_data = {
        "niche_trends": ["natural skincare", "minimalist makeup"],
        "content_strategies": ["how-to videos", "product reviews"]
    }
    store_details = {
        "store_name": "Beauty Bliss",
        "brand_voice": "elegant and approachable",
        "fun_facts": "We use organic ingredients",
        "signature_products": "Herbal face masks"
    }
    visual_captions = ["a bright modern interior", "a stunning product display"]
    
    alternatives = master_reasoning_agent(niche, research_data, store_details, visual_captions)
    print("Alternatives:")
    print(json.dumps(alternatives, indent=2))

from config import Config
from exceptions import APIError
from testing import mock_text_generation, should_mock
from logger import logger
from openai import OpenAI

def research_agent(niche: str) -> dict:
    logger.info(f"Starting research agent for: {niche}")
    
    if should_mock():
        logger.debug("Using mock research data")
        return {
            "niche_trends": "\n".join([
                "Mock Trend 1: Virtual Fitness Classes",
                "Mock Trend 2: AI-Powered Workouts"
            ]),
            "content_trends": "\n".join([
                "Content Strategy 1: Before/After Transformations",
                "Content Strategy 2: 30-Second Exercise Tutorials"
            ])
        }
    
    try:
        client = OpenAI(api_key=Config.OPENAI_API_KEY)
        
        # Trend research
        niche_response = client.chat.completions.create(
            model=Config.MODEL,
            messages=[{
                "role": "user",
                "content": f"Identify top trends in {niche} for social media. Use bullet points."
            }]
        )
        
        # Content strategies
        content_response = client.chat.completions.create(
            model=Config.MODEL,
            messages=[{
                "role": "user",
                "content": f"Suggest viral content strategies for {niche} on Instagram."
            }]
        )
        
        return {
            "niche_trends": niche_response.choices[0].message.content,
            "content_trends": content_response.choices[0].message.content
        }
        
    except Exception as e:
        logger.error(f"Research failed: {str(e)}")
        raise APIError("Research agent failed") from e
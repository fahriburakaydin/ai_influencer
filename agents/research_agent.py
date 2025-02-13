from config import Config
from exceptions import APIError
from testing import mock_text_generation, should_mock
from logger import logger
from openai import OpenAI


def parse_research(text: str) -> dict:
    """Convert raw text response to structured data"""
    sections = text.split("\n\n")
    return {
        "niche_trends": sections[0].split("\n")[1:],
        "content_trends": sections[1].split("\n")[1:]
    }

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
        
        if Config.TEST_MODE:
            return {
                "niche_trends": "1. Micro-workouts (5-min routines)\n2. Recovery tech (percussion massagers)",
                "content_trends": "1. Progress comparison videos\n2. Myth-busting reels"
            }
            
        # More focused research prompt    
        research_prompt = f"""
        Analyze {niche} industry trends for social media content creation.
        Provide 5 specific, actionable trends in this format:
        
        Niche Trends:
        1. [Specific trend 1]
        2. [Specific trend 2]
        
        Content Strategies:
        1. [Content type 1 with example]
        2. [Content type 2 with example]
        """
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": research_prompt}],
            temperature=0.7  # More creative
        )
        
        return parse_research(response.choices[0].message.content)
        
    except Exception as e:
        logger.error(f"Research failed: {str(e)}")
        raise APIError("Research agent failed") from e
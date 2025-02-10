from typing import Dict
from config import Config
from exceptions import ValidationError
from logger import logger

def content_planner(research_data: Dict) -> Dict:
    logger.info("Starting content planning")
    
    try:
        # Validate input
        if not research_data:
            raise ValidationError("Empty research data")
            
        if not all(key in research_data for key in ["niche_trends", "content_trends"]):
            raise ValidationError("Invalid research data format")
            
        # Extract first trend from each category
        niche_trend = research_data["niche_trends"].splitlines()[0]
        content_trend = research_data["content_trends"].splitlines()[0]
        
        return {
            "content_plan": [
                f"Post about {niche_trend}",
                f"Post using {content_trend}"
            ]
        }
        
    except Exception as e:
        logger.error(f"Content planning failed: {str(e)}")
        raise ValidationError("Failed to create content plan") from e
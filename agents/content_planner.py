# agents/content_planner.py
from typing import Dict
from config import Config
from exceptions import ValidationError
from logger import logger
from pydantic import ValidationError

def content_planner(research_data: Dict) -> Dict:
    logger.info("Starting content planning")
    
    try:
        if not research_data:
            raise ValidationError("Empty research data")
        
        if not isinstance(research_data, dict):
            raise ValidationError("Research data must be a dictionary")      

        # Updated required keys to match the new research agent output.
        required_keys = {"niche_trends", "content_strategies"}
        if not required_keys.issubset(research_data.keys()):
            missing = required_keys - research_data.keys()
            raise ValidationError(f"Missing research keys: {missing}")

        # Combine trends and strategies
        combined_ideas = []
        for niche_trend in research_data["niche_trends"]:
            for content_trend in research_data["content_strategies"]:
                combined_ideas.append(f"{niche_trend} using {content_trend}")
        
        return {
            "content_plan": combined_ideas[:Config.NUM_ALTERNATIVES]  # Return top N combination 
        }
        
    except Exception as e:
        logger.error(f"Content planning failed: {str(e)}")
        raise ValidationError("Failed to create content plan") from e

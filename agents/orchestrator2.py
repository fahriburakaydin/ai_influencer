# simple_orchestrator.py

import time
import json
from logger import logger  # Importing our logging tool to record actions
from agents.research_agent import research_agent  # Agent to gather research data
from agents.content_planner import content_planner  # Agent to plan content from research data
from agents.image_generator import generate_image  # Agent to generate an image URL
from agents.caption_generator import generate_caption  # Agent to generate an Instagram caption

class Orchestrator:
    def __init__(self, max_retries=2, retry_delay=2):
        """
        Initialize the orchestrator.
        
        :param max_retries: Maximum number of times to retry an agent call if it fails.
        :param retry_delay: Time (in seconds) to wait between retry attempts.
        """
        self.max_retries = max_retries
        self.retry_delay = retry_delay

    def run_workflow(self, niche: str) -> dict:
        """
        Run the complete content creation workflow for a given niche.
        """
        logger.info(f"Starting workflow for niche: {niche}")

        # 1. Research: Get trends and insights for the niche.
        research_data = self._execute_with_retry("ResearchAgent", research_agent, niche)
        logger.info(f"Research data received: {research_data}")

        # 2. Content Planning: Create content ideas based on research.
        content_plan = self._execute_with_retry("ContentPlanner", content_planner, research_data)
        logger.info(f"Content plan received: {content_plan}")

        # 3. For each idea in the content plan, generate an image and a caption.
        posts = []
        for idea in content_plan["content_plan"]:
            # Generate an image URL for this idea.
            image_url = self._execute_with_retry("ImageGenerator", generate_image, idea)
            # Generate an Instagram caption for this idea.
            caption = self._execute_with_retry("CaptionGenerator", generate_caption, idea)
            # Store the complete post data.
            posts.append({
                "idea": idea,
                "image": image_url,
                "caption": caption
            })
            logger.info(f"Post created: {posts[-1]}")

        logger.info("Workflow completed successfully")
        return {"posts": posts}

    def _execute_with_retry(self, agent_name: str, function, input_data):
        """
        Execute an agent function and retry if it fails.
        
        :param agent_name: Name of the agent (for logging).
        :param function: The agent function to call.
        :param input_data: Data to pass to the agent function.
        :return: The result from the agent function.
        """
        attempts = 0
        while attempts < self.max_retries:
            try:
                logger.info(f"Calling {agent_name} (attempt {attempts+1}) with input: {input_data}")
                result = function(input_data)  # Call the agent function with the provided input.
                logger.info(f"{agent_name} succeeded with result: {result}")
                return result  # Return result if successful.
            except Exception as e:
                attempts += 1
                logger.error(f"{agent_name} failed on attempt {attempts} with error: {e}")
                time.sleep(self.retry_delay)  # Wait before trying again.
        # If all attempts fail, raise an exception.
        raise Exception(f"{agent_name} failed after {self.max_retries} attempts")

# This block runs the workflow if this file is executed directly.
if __name__ == "__main__":
    niche = "Fitness and Health"  # Example niche
    orchestrator = Orchestrator()
    try:
        result = orchestrator.run_workflow(niche)
        print("Final workflow result:")
        print(json.dumps(result, indent=2))
    except Exception as e:
        logger.error(f"Workflow failed: {e}")

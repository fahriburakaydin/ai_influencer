import time
import json
from logger import logger  # Importing our logging tool to record actions
from agents.research_agent_crew import research_agent  # Agent to gather research data
from agents.content_planner import content_planner  # Agent to plan content from research data
from agents.image_generator import generate_image  # Agent to generate an image URL
from agents.caption_generator import generate_caption  # Agent to generate an Instagram caption
import faiss
import numpy as np
from faiss_memory import load_faiss_index, query_faiss_index, model  # Import Faiss-related functions
from config import Config


class Orchestrator:

    

    def __init__(self, max_retries=2, retry_delay=2, index_file='posts.index'):
        """
        Initialize the orchestrator.
        
        :param max_retries: Maximum number of times to retry an agent call if it fails.
        :param retry_delay: Time (in seconds) to wait between retry attempts.
        :param index_file: Path to the Faiss index file.
        """
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.index_file = index_file
        self.index = load_faiss_index(index_file)  # Load Faiss index for similarity checks
        self.distance_threshold = Config.DISTANCE_THRESHOLD

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

        # 3. For each idea in the content plan, check for similarity and generate content.
        posts = []
        for idea in content_plan["content_plan"]:
            # Check similarity of the idea with the Faiss index
            is_similar = self._check_similarity_with_memory(idea)
            
            if is_similar:
                logger.info(f"Post idea is too similar to previous posts: {idea}")
                # Implement logic to either tweak or reject idea based on business rules
                continue  # Skip or handle differently (like suggesting a variation)
            
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
                result = function(input_data)
                logger.info(f"{agent_name} succeeded with result: {result}")
                return result
            except APIError as ae:
                logger.error(f"{agent_name} failed with APIError: {ae}")
                # Potentially handle differently or parse the error message
            except ValidationError as ve:
                logger.error(f"{agent_name} failed with ValidationError: {ve}")
                # Might skip retry if input is invalid
                break
            except Exception as e:
                logger.error(f"{agent_name} failed with an unexpected error: {e}")
                
            attempts += 1
            time.sleep(self.retry_delay)

        raise Exception(f"{agent_name} failed after {self.max_retries} attempts")

    def _check_similarity_with_memory(self, new_idea):
        """
        Check if a new content idea is too similar to existing posts in memory.
        """
        query_text = new_idea  # You can adapt this to be more specific (e.g., using the caption).
        indices, distances = query_faiss_index(query_text, self.index, top_k=3)
        
        # If the distance is below a certain threshold, consider it too similar
        if distances[0] < self.distance_threshold:  # You can adjust the threshold value based on your requirements
            return True  # Too similar
        return False

# This block runs the workflow if this file is executed directly.
if __name__ == "__main__":
    niche = "beauty"  # Example niche
    orchestrator = Orchestrator()
    try:
        result = orchestrator.run_workflow(niche)
        print("Final workflow result:")
        print(json.dumps(result, indent=2))
    except Exception as e:
        logger.error(f"Workflow failed: {e}")
 

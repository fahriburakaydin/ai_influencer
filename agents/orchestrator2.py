import time
import json
from logger import logger
from database import get_store, get_store_images  # ✅ Import function to fetch store details
from agents.research_agent_crew import research_agent
from agents.content_planner import content_planner
from agents.image_generator import generate_image
from agents.caption_generator import generate_caption
import faiss
import numpy as np
from faiss_memory import load_faiss_index, query_faiss_index, model
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
        self.index = load_faiss_index(index_file)
        self.distance_threshold = Config.DISTANCE_THRESHOLD

    def run_workflow(self, niche: str) -> dict:
        """
        Run the complete content creation workflow for a given niche, now personalized with store profile data.
        """
        logger.info(f"Starting workflow for niche: {niche}")

        #  1. Fetch store details
        store = get_store()
        store_images = get_store_images()  # Retrieve images + descriptions
        if not store:
            logger.warning("No store profile found. Proceeding without personalization.")
            store_details = {}
        else:
            store_details = {
                "store_name": store[1],
                "address": store[2],
                "brand_voice": store[3],
                "fun_facts": store[4],
                "signature_products": store[5],
                "store_images": store_images  # Include images & descriptions
            }
            logger.info(f"Using store profile: {store_details}")

        #  2. Research: Get niche trends, passing store details
        research_data = self._execute_with_retry("ResearchAgent", research_agent, niche, store_details)
        logger.info(f"Research data received: {research_data}")

        #  3. Content Planning: Generate content strategies based on research + store details
        content_plan = self._execute_with_retry("ContentPlanner", content_planner, research_data, store_details)
        logger.info(f"Content plan received: {content_plan}")

        #  4. Generate posts
        posts = []
        for idea in content_plan["content_plan"]:
            # Check similarity with memory
            is_similar = self._check_similarity_with_memory(idea)
            if is_similar:
                logger.info(f"Post idea too similar to previous posts: {idea}")
                continue

            #  5. Generate image & caption using store details
            image_url = self._execute_with_retry("ImageGenerator", generate_image, idea, store_details)
            caption = self._execute_with_retry("CaptionGenerator", generate_caption, idea, store_details)

            #  6. Store final post
            posts.append({
                "idea": idea,
                "image": image_url,
                "caption": caption
            })
            logger.info(f"Post created: {posts[-1]}")

        logger.info("Workflow completed successfully")
        return {"posts": posts}

    def _execute_with_retry(self, agent_name: str, function, input_data, store_details):
        """
        Execute an agent function with retry logic, passing store details.

        :param agent_name: Name of the agent (for logging).
        :param function: The agent function to call.
        :param input_data: Data to pass to the agent function.
        :return: The result from the agent function.
        """
        attempts = 0
        while attempts < self.max_retries:
            try:
                logger.info(f"Calling {agent_name} (attempt {attempts+1}) with input: {input_data}")
                result = function(input_data, store_details)  # ✅ Pass store details to AI agent
                logger.info(f"{agent_name} succeeded with result: {result}")
                return result
            except Exception as e:
                logger.error(f"{agent_name} failed: {e}")

            attempts += 1
            time.sleep(self.retry_delay)

        raise Exception(f"{agent_name} failed after {self.max_retries} attempts")

    def _check_similarity_with_memory(self, new_idea):
        """
        Check if a new content idea is too similar to existing posts.
        """
        query_text = new_idea
        indices, distances = query_faiss_index(query_text, self.index, top_k=3)

        if distances[0] < self.distance_threshold:
            return True  # Too similar
        return False


if __name__ == "__main__":
    niche = "beauty"  # Example niche
    orchestrator = Orchestrator()
    try:
        result = orchestrator.run_workflow(niche)
        print("Final workflow result:")
        print(json.dumps(result, indent=2))
    except Exception as e:
        logger.error(f"Workflow failed: {e}")

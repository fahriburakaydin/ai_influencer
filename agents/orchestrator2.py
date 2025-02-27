from flask import Flask, session
import time
import json
from logger import logger
from database import get_store, get_store_images, save_post
from agents.research_agent_crew import research_agent
from agents.master_reasoning_agent import master_reasoning_agent
from agents.image_generator import generate_image
from faiss_memory import load_faiss_index
from config import Config

class Orchestrator:
    def __init__(self, max_retries=2, retry_delay=2, index_file='posts.index'):
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.index_file = index_file
        self.index = load_faiss_index(index_file)
        self.distance_threshold = Config.DISTANCE_THRESHOLD

    def run_workflow(self, niche: str) -> dict:
        logger.info(f"Starting workflow for niche: {niche}")

        # 1. Fetch store details and images
        store = get_store()
        store_images = get_store_images()  # List of image records with their paths & descriptions
        if not store:
            logger.warning("No store profile found. Proceeding without personalization.")
            store_details = {}
        else:
            store_details = {
                "store_name": store[1],
                "address": store[2],
                "brand_voice": store[3],
                "fun_facts": store[4],
                "signature_products": store[5]
            }
            logger.info(f"Using store profile: {store_details}")

        # 2. Research: Get niche trends & content strategies
        research_data = self._execute_with_retry("ResearchAgent", research_agent, niche, store_details)
        logger.info(f"Research data received: {research_data}")

        # 3. Gather visual captions from store images (if available)
        visual_captions = [img.get("visual_caption", "") for img in store_images if img.get("visual_caption")]

        # 4. Use the Master Reasoning Agent to generate alternative strategies and prompts
        alternatives = master_reasoning_agent(niche, research_data, store_details, visual_captions)
        logger.info(f"Master Reasoning output alternatives: {alternatives}")

        # 5. For each alternative, generate the image using its image prompt.
        #    The caption is taken directly from the alternative.
        posts = []
        for alt in alternatives:
            image_url = self._execute_with_retry("ImageGenerator", generate_image, alt.get("image_prompt", ""), store_details)
            caption = alt.get("caption_prompt", "")
            post = {
                "idea": alt.get("final_narrative", ""),
                "image": image_url,
                "caption": caption
            }
            posts.append(post)
        
        # Store the full list of complete posts for review.
        session['pending_posts'] = posts
        logger.info(f"Complete post alternatives stored for review: {posts}")
        return {"pending_posts": posts}

    def _execute_with_retry(self, agent_name: str, function, *args, **kwargs):
        attempts = 0
        while attempts < self.max_retries:
            try:
                logger.info(f"Calling {agent_name} (attempt {attempts+1}) with args: {args}, kwargs: {kwargs}")
                result = function(*args, **kwargs)
                logger.info(f"{agent_name} succeeded with result: {result}")
                return result
            except Exception as e:
                logger.error(f"{agent_name} failed: {e}")
                attempts += 1
                time.sleep(self.retry_delay)
        raise Exception(f"{agent_name} failed after {self.max_retries} attempts")

# For testing purposes, wrap execution in a Flask test request context
if __name__ == "__main__":
    app = Flask(__name__)
    app.secret_key = "your_secret_key"  # Ensure a secret key is set for session

    with app.test_request_context():
        niche = "beauty"
        orchestrator = Orchestrator()
        try:
            result = orchestrator.run_workflow(niche)
            print("Workflow alternatives:")
            print(json.dumps(result, indent=2))
        except Exception as e:
            logger.error(f"Workflow failed: {e}")

import logging
from agents.research_agent import research_agent
from agents.content_planner import content_planner
from agents.image_generator import generate_image
from agents.caption_generator import generate_caption
from database import init_db, save_post


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Main CLI workflow"""
    print("\n=== AI Influencer Creator ===")
    try:
        init_db()  # Should run FIRST before anything else
        print("DB initiated.")
    except Exception as e:
        print(f"CRITICAL: Database setup failed - {str(e)}")
        return

    try:
        print("\n=== AI Influencer Creator ===")
        niche = input("Enter your niche/topic: ").strip()
        
        logger.info("Starting research phase...")
        research = research_agent(niche)
        
        logger.info("Planning content...")
        plan = content_planner(research)
        
        print("\n=== Generated Plan ===")
        for i, post in enumerate(plan["content_plan"], 1):
            print(f"\nPost {i}: {post}")
            
            logger.info(f"Generating assets for Post {i}")
            image_url = generate_image(post)
            caption = generate_caption(post)
            
            print(f"\nImage URL: {image_url}")
            print(f"Caption:\n{caption}")

            save_post(niche, post, image_url, caption)
            print("post_saved in db")
            
        print("\n=== Process Complete ===")
        print("Check 'outputs/' directory for generated files")
        
    except Exception as e:
        logger.error(f"System failure: {str(e)}")
        print("\n⚠️  Critical error occurred. Check logs for details.")

if __name__ == "__main__":
    main()
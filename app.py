from flask import Flask, render_template, request, redirect, url_for
from agents.research_agent import research_agent
from agents.content_planner import content_planner
from agents.image_generator import generate_image
from agents.caption_generator import generate_caption
from database import init_db, save_post
from exceptions import AppError
from logger import logger
from config import Config
from instagram_poster import InstagramPoster

logger.info("Application started successfully")

app = Flask(__name__)
init_db()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/create', methods=['POST'])
def create_post():
    try:
        niche = request.form.get('niche', '').strip()
        if not niche:
            return redirect(url_for('home'))
            
        logger.info(f"Starting workflow for niche: {niche}")
        
        # Agent workflow
        research = research_agent(niche)
        plan = content_planner(research)
        logger.debug(f"Content Plan: {plan}")

        posts = []
        poster = InstagramPoster()

        for idea in plan["content_plan"]:
            image_url = generate_image(idea)
            caption = generate_caption(idea)
            logger.debug(f"Image URL: {image_url}, Caption: {caption}")
            logger.debug(f"Data types - Niche: {type(niche)}, Post Idea: {type(idea)}, Image URL: {type(image_url)}, Caption: {type(caption)}")
            save_post(niche, idea, image_url, caption)
            posts.append({
                "image": image_url,
                "caption": caption,
                "idea": idea
            })
            if poster.post_to_instagram(image_url, caption):
                logger.info("Posted to Instagram successfully!")
            else:
             logger.warning("Failed to post to Instagram")

        
        return render_template('results.html', posts=posts)
        
    except AppError as e:
        logger.error(f"Workflow failed: {str(e)}")
        return render_template('error.html', message=str(e)), 500
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return render_template('error.html', message="An unexpected error occurred"), 500

if __name__ == '__main__':
    app.run(debug=Config.TEST_MODE)
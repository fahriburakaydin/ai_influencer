from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from agents.research_agent import research_agent
from agents.content_planner import content_planner
from agents.image_generator import generate_image
from agents.caption_generator import generate_caption
from database import init_db, save_post
from exceptions import AppError
from logger import logger
from config import Config
from instagram_poster import InstagramPoster, InstagrApiPoster
from instagrapi.exceptions import ChallengeRequired
import os
import time
from datetime import datetime
from agents.orchestrator2 import Orchestrator  


logger.info("Application started successfully")

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")

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
            
        poster = InstagrApiPoster()
        code = session.pop('2fa_code', None)

        orchestrator = Orchestrator()
        
        try:
            login_success = poster.login(code=code)
        except ChallengeRequired:
            return redirect(url_for('show_2fa_form'))
            
        if not login_success:
            error_msg = "Invalid 2FA code. Please try again." if code else "Login failed"
            return render_template('2fa.html', error=error_msg)
            
        # Start processing
        start_time = datetime.now()
        logger.info(f"Started processing niche: {niche}")
       
        # Get full workflow result
        workflow_result  = orchestrator.run_workflow(niche)
        
        posts = []
        failed_posts = []
        
        for post in workflow_result.get("posts", []):
            idea = post.get("idea")
            image_url = post.get("image")
            caption = post.get("caption")
            try:
                save_post(niche, idea, image_url, caption)
                if Config.INSTAGRAM_TEST:
                    logger.info("INSTAGRAM_TEST enabled, skipping Instagram posting.")
                    posts.append({"image": image_url, "caption": caption})

                else:
                    if poster.post_content(image_url, caption):
                        posts.append({"image": image_url, "caption": caption})
                    else:
                        failed_posts.append({"image": image_url, "caption": caption})
                        logger.warning(f"Failed to post: {idea}")
                        
            except Exception as e:
                logger.error(f"Error processing post: {str(e)}")
                failed_posts.append({"error": str(e)})
        
        return render_template('results.html', 
                               posts=posts, 
                               failed_posts=failed_posts,
                               time_taken=str(datetime.now() - start_time))
    
    except ChallengeRequired:
        logger.info("2FA required - redirecting")
        return redirect(url_for('show_2fa_form'))
    except Exception as e:
        logger.error(f"Workflow failed: {str(e)}", exc_info=True)
        return render_template('error.html', 
                            message="Failed to coordinate agents. Details in logs."), 500

@app.route('/2fa', methods=['GET', 'POST'])
def show_2fa_form():
    if request.method == 'POST':
        session['2fa_code'] = request.form.get('2fa_code', '')
        return redirect(url_for('create_post'))
    return render_template('2fa.html', error=request.args.get('error'))

@app.route('/verify-2fa', methods=['POST'])
def verify_2fa():
    session['2fa_code'] = request.form.get('2fa_code', '')
    return redirect(url_for('create_post'))

@app.route('/status')
def check_status():
    return jsonify({"status": "processing"})

if __name__ == '__main__':
    app.run(debug=Config.TEST_MODE)
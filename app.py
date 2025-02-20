from flask import Flask, render_template, request, redirect, url_for, session, jsonify , send_from_directory

from database import init_db, save_post, save_store, get_store, get_store_images, save_store_image
from exceptions import AppError
from logger import logger
from config import Config
from instagram_poster import InstagramPoster, InstagrApiPoster
from instagrapi.exceptions import ChallengeRequired
import os
import time
from datetime import datetime
from agents.orchestrator2 import Orchestrator  
from werkzeug.utils import secure_filename


logger.info("Application started successfully")

UPLOAD_FOLDER = 'static/uploads' # Directory to store images

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


# Initialize the database
init_db()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/store-profile', methods=['GET', 'POST'])
def store_profile():
    """
    Handles store profile creation and updates.
    """
    if request.method == 'POST':
        store_name = request.form.get('store_name')
        address = request.form.get('address')
        brand_voice = request.form.get('brand_voice')
        fun_facts = request.form.get('fun_facts')
        signature_products = request.form.get('signature_products')

        save_store(store_name, address, brand_voice, fun_facts, signature_products)

        return redirect(url_for('store_profile'))

    # Load existing store data and images
    store = get_store()
    store_images = get_store_images()
    return render_template('store_profile.html', store=store, store_images=store_images)

@app.route('/upload-image', methods=['POST'])
def upload_image():
    """
    Handles image uploads for store profile.
    """
    file = request.files['file']
    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file_path = file_path.replace("\\", "/") # Convert Windows-style backslashes to forward slashes
        file.save(file_path)

        store = get_store()
        if store:
            save_store_image(store[0], file_path)

    return redirect(url_for('store_profile'))


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/create', methods=['POST'])
def create_post():
    """
    1. Receives the niche from the user.
    2. Logs in to Instagram (with optional 2FA).
    3. Runs the orchestrator to generate posts (images + captions).
    4. Stores generated posts in session (pending_posts).
    5. Redirects the user to review the posts at /review.
    """
    try:
        niche = request.form.get('niche', '').strip().replace(' ', '_')
        if not niche:
            return redirect(url_for('home'))

        # Prepare the InstagramPoster (or InstagrApiPoster) for later use
        poster = InstagrApiPoster()
        code = session.pop('2fa_code', None)  # If user has just submitted 2FA

        # Instantiate the orchestrator
        orchestrator = Orchestrator()

        # Handle Instagram login (including 2FA)
        try:
            login_success = poster.login(code=code)
        except ChallengeRequired:
            # If Instagram triggers a challenge flow, redirect to 2FA
            return redirect(url_for('show_2fa_form'))

        if not login_success:
            # If login fails or code is incorrect
            error_msg = "Invalid 2FA code. Please try again." if code else "Login failed."
            return render_template('2fa.html', error=error_msg)

        # Start timing
        session['start_time'] = time.time()
        logger.info(f"Started processing niche: {niche}")

        # Generate content using the Orchestrator
        workflow_result = orchestrator.run_workflow(niche)
        pending_posts = workflow_result.get("posts", [])

        # Store the posts in session for user review
        session['pending_posts'] = pending_posts
        session['niche'] = niche  # Store niche if you want to save it later

        # Redirect to review page
        return redirect(url_for('review_posts'))

    except ChallengeRequired:
        logger.info("2FA required - redirecting user to /2fa")
        return redirect(url_for('show_2fa_form'))
    except Exception as e:
        logger.error(f"Workflow failed: {str(e)}", exc_info=True)
        return render_template('error.html', message="Failed to coordinate agents. Details in logs."), 500


@app.route('/review', methods=['GET', 'POST'])
def review_posts():
    """
    GET: Displays pending posts for user to review/edit/remove.
    POST: Accepts user edits/removals, updates session, redirects to finalize.
    """
    if request.method == 'POST':
        # Retrieve the pending posts from session
        posts = session.get('pending_posts', [])

        updated_posts = []
        # We'll loop over the posts using index references (i)
        for i, post in enumerate(posts):
            # Get new caption (if any)
            form_caption = request.form.get(f"caption_{i}", post['caption'])

            # Check if user wants to remove this post
            remove_flag = request.form.get(f"delete_{i}", "off")
            if remove_flag == "on":
                # Skip adding to updated_posts, effectively removing it
                continue

            # Otherwise, keep the post but update the caption
            updated_posts.append({
                "idea": post["idea"],
                "image": post["image"],
                "caption": form_caption
            })

        # Store the updated list back into session
        session['pending_posts'] = updated_posts

        return redirect(url_for('finalize_posts'))

    # If GET: Display the review page
    posts = session.get('pending_posts', [])
    return render_template('review.html', posts=posts)


@app.route('/finalize', methods=['GET', 'POST'])
def finalize_posts():
    """
    - Grabs the user-approved (and possibly edited) posts from session.
    - Attempts to post them to Instagram.
    - Saves to the database if successful.
    - Renders the final results page (results.html).
    """
    # Retrieve final posts from session
    posts = session.pop('pending_posts', [])
    niche = session.pop('niche', 'unknown')  # If you want to store the niche in DB

    if not posts:
        # If user removed everything or there's nothing to post
        return render_template(
            'results.html',
            posts=[],
            failed_posts=[],
            time_taken="0:00:00"
        )

    # Prepare to post
    posted = []
    failed = []
    poster = InstagrApiPoster()

    # Post each user-approved post
    for post in posts:
        idea = post["idea"]
        image_url = post["image"]
        caption = post["caption"]
        try:
            success = False
            if Config.INSTAGRAM_TEST:
                # If in TEST mode, skip actual posting
                logger.info("INSTAGRAM_TEST = True; skipping actual Instagram posting.")
                success = True
            else:
                # Actually call Instagram
                success = poster.post_content(image_url, caption)

            # Save to DB if posted successfully (or if you want to store them always)
            if success:
                save_post(niche, idea, image_url, caption)
                posted.append(post)
            else:
                logger.warning(f"Failed to post: {idea}")
                failed.append(post)
        except Exception as e:
            logger.error(f"Error posting to Instagram: {str(e)}")
            failed.append(post)

    # Calculate time taken
    start_time = session.pop('start_time', None)
    if start_time:
        elapsed = time.time() - start_time
        time_taken = str(datetime.fromtimestamp(elapsed) - datetime(1970,1,1))
    else:
        time_taken = "N/A"

    # Render final results page
    return render_template(
        'results.html',
        posts=posted,
        failed_posts=failed,
        time_taken=time_taken
    )

@app.route('/2fa', methods=['GET', 'POST'])
def show_2fa_form():
    """
    If user runs into 2FA challenge, they come here.
    They submit a '2fa_code', which we store in session, then
    redirect back to create_post.
    """
    if request.method == 'POST':
        session['2fa_code'] = request.form.get('2fa_code', '')
        return redirect(url_for('create_post'))
    return render_template('2fa.html', error=request.args.get('error'))


@app.route('/verify-2fa', methods=['POST'])
def verify_2fa():
    """
    Additional endpoint if you prefer a separate route to handle form submission.
    """
    session['2fa_code'] = request.form.get('2fa_code', '')
    return redirect(url_for('create_post'))


@app.route('/status')
def check_status():
    """
    Simple status endpoint for any long-running tasks or AJAX-based checks.
    Right now, it just returns "processing".
    """
    return jsonify({"status": "processing"})


if __name__ == '__main__':
    # Note: Set debug to False in production
    app.run(debug=Config.TEST_MODE)
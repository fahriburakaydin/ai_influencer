import sqlite3
from datetime import datetime
from config import Config
from exceptions import DatabaseError
from logger import logger

def init_db():
    try:
        conn = sqlite3.connect('posts.db')
        c = conn.cursor()
        
        c.execute('''CREATE TABLE IF NOT EXISTS posts
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      niche TEXT NOT NULL,
                      post_idea TEXT NOT NULL,
                      image_url TEXT NOT NULL,
                      caption TEXT NOT NULL,
                      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        
        conn.commit()
        logger.info("Database initialized successfully")
        
    except sqlite3.Error as e:
        logger.error(f"Database initialization failed: {str(e)}")
        raise DatabaseError("Failed to initialize database") from e
    finally:
        if conn:
            conn.close()

def save_post(niche: str, post_idea: str, image_url, caption: str):
    if Config.TEST_MODE:
        logger.debug("TEST_MODE: Skipping database save")
        return
        
    try:
        # Convert all inputs to strings explicitly
        conn = sqlite3.connect('posts.db')
        c = conn.cursor()
        
        c.execute('''INSERT INTO posts 
                     (niche, post_idea, image_url, caption, created_at)
                     VALUES (?,?,?,?,?)''',
                  (
                      str(niche), 
                      str(post_idea), 
                      str(image_url),  # Ensure this is a string
                      str(caption), 
                      datetime.now().isoformat()
                  ))
        
        conn.commit()
        logger.info(f"Saved post: {post_idea[:50]}...")
        
    except sqlite3.Error as e:
        logger.error(f"Database save failed: {str(e)}")
        raise DatabaseError("Failed to save post") from e
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise DatabaseError("Unexpected database error") from e
    finally:
        if conn:
            conn.close()
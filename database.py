import sqlite3
from datetime import datetime
from config import Config
from exceptions import DatabaseError
from logger import logger
import os

def init_db():
    try:
        conn = sqlite3.connect('posts.db')
        c = conn.cursor()
        #Create the posts table if it doesn't exist
        c.execute('''CREATE TABLE IF NOT EXISTS posts
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      niche TEXT NOT NULL,
                      post_idea TEXT NOT NULL,
                      image_url TEXT NOT NULL,
                      caption TEXT NOT NULL,
                      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        
        # Create the stores table if it doesn't exist
        c.execute('''
            CREATE TABLE IF NOT EXISTS stores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                store_name TEXT NOT NULL,
                address TEXT,
                brand_voice TEXT,
                fun_facts TEXT,
                signature_products TEXT
            )
        ''')
        
        # Create table for uploaded images
        c.execute('''CREATE TABLE IF NOT EXISTS store_images (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        store_id INTEGER NOT NULL,
                        image_path TEXT NOT NULL,
                        description TEXT DEFAULT '',  -- New column for image descriptions
                        FOREIGN KEY(store_id) REFERENCES stores(id)
                    )''')
        
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


def save_store(store_name: str, address: str, brand_voice: str, fun_facts: str, signature_products: str):
    """ Saves or updates store profile data """
    try:
        conn = sqlite3.connect('posts.db')
        c = conn.cursor()

        # Check if a store profile already exists
        c.execute("SELECT id FROM stores LIMIT 1")
        existing = c.fetchone()

        if existing:
            c.execute('''
                UPDATE stores SET 
                    store_name=?, address=?, brand_voice=?, 
                    fun_facts=?, signature_products=? WHERE id=?
            ''', (store_name, address, brand_voice, fun_facts, signature_products, existing[0]))
        else:
            c.execute('''
                INSERT INTO stores 
                    (store_name, address, brand_voice, fun_facts, signature_products)
                VALUES (?, ?, ?, ?, ?)
            ''', (store_name, address, brand_voice, fun_facts, signature_products))
        
        conn.commit()
        logger.info("Store profile saved successfully")

    except sqlite3.Error as e:
        logger.error(f"Failed to save store profile: {str(e)}")
        raise DatabaseError("Failed to save store profile") from e
    finally:
        if conn:
            conn.close()

def save_store_image(store_id, image_path, description=""):
    """
    Saves an uploaded image with an optional description.
    """
    try:
        conn = sqlite3.connect('posts.db')
        c = conn.cursor()
        
        c.execute('''INSERT INTO store_images (store_id, image_path, description) 
                     VALUES (?, ?, ?)''', (store_id, image_path, description))
        
        conn.commit()
        logger.info(f"Saved image to DB: {image_path} with description: {description}")

    except sqlite3.Error as e:
        logger.error(f"Failed to save image: {str(e)}")
    finally:
        if conn:
            conn.close()

def get_store():
    """ Retrieve the store details """
    conn = sqlite3.connect('posts.db')
    c = conn.cursor()
    c.execute("SELECT * FROM stores LIMIT 1")
    store = c.fetchone()
    logger.info(f"Fetched store details: {store}")
    conn.close()
    return store

def get_store_images():
    """
    Retrieves store images along with their descriptions.
    """
    try:
        conn = sqlite3.connect('posts.db')
        c = conn.cursor()
        c.execute('''SELECT id, store_id, image_path, description FROM store_images''')
        images = c.fetchall()
        logger.info(f"Fetched store images: {images}")  #  Log images in the correct function
        return [{"id": img[0], "store_id": img[1], "image_path": img[2], "description": img[3]} for img in images]

    except sqlite3.Error as e:
        logger.error(f"Failed to fetch store images: {str(e)}")
        return []
    finally:
        if conn:
            conn.close()

def delete_store_image(image_id):
    try:
        conn = sqlite3.connect('posts.db')
        c = conn.cursor()
        # Retrieve the file path before deleting the record
        c.execute('SELECT image_path FROM store_images WHERE id=?', (image_id,))
        row = c.fetchone()
        if row:
            image_path = row[0]
            # Delete the record from the database
            c.execute('DELETE FROM store_images WHERE id=?', (image_id,))
            conn.commit()
            logger.info(f"Deleted image record: {image_path}")
            # Optionally, delete the file from the filesystem
            if os.path.exists(image_path):
                os.remove(image_path)
        return True
    except Exception as e:
        logger.error(f"Error deleting image: {str(e)}")
        return False
    finally:
        if conn:
            conn.close()

def get_image_by_id(image_id):
    try:
        conn = sqlite3.connect('posts.db')
        c = conn.cursor()
        c.execute('SELECT id, store_id, image_path, description FROM store_images WHERE id=?', (image_id,))
        row = c.fetchone()
        if row:
            return {"id": row[0], "store_id": row[1], "image_path": row[2], "description": row[3]}
        return None
    except Exception as e:
        logger.error(f"Error fetching image: {str(e)}")
        return None
    finally:
        if conn:
            conn.close()

def update_store_image(image_id, new_description):
    try:
        conn = sqlite3.connect('posts.db')
        c = conn.cursor()
        c.execute('UPDATE store_images SET description=? WHERE id=?', (new_description, image_id))
        conn.commit()
        logger.info(f"Updated image {image_id} description")
    except Exception as e:
        logger.error(f"Error updating image description: {str(e)}")
    finally:
        if conn:
            conn.close()
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    TEST_MODE = os.getenv("TEST_MODE", "False").lower() == "true"
    INSTAGRAM_TEST = os.getenv("INSTAGRAM_TEST", "false").lower() == "true"
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")
    
    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
    
    INSTAGRAM_ACCOUNT_ID = os.getenv("INSTAGRAM_ACCOUNT_ID")
    INSTAGRAM_ACCESS_TOKEN = os.getenv("INSTAGRAM_ACCESS_TOKEN")

    INSTAGRAM_USERNAME=os.getenv("INSTAGRAM_USERNAME")
    INSTAGRAM_PASSWORD=os.getenv("INSTAGRAM_USERNAME")

    INSTAGRAM_SESSION_FILE = os.getenv("INSTAGRAM_SESSION_FILE", "instagram_session.json")

    DEEPSEK_API_ENDPOINT = os.getenv("DEEPSEEK_API_ENDPOINT")

    MODEL=os.getenv("MODEL")    
    REASON_MODEL=os.getenv("REASON_MODEL")

    DISTANCE_THRESHOLD=0.5
    NUM_ALTERNATIVES=2
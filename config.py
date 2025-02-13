import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    TEST_MODE = os.getenv("TEST_MODE", "False").lower() == "true"
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")
    MODEL=os.getenv("MODEL")
    INSTAGRAM_ACCOUNT_ID = os.getenv("INSTAGRAM_ACCOUNT_ID")
    INSTAGRAM_ACCESS_TOKEN = os.getenv("INSTAGRAM_ACCESS_TOKEN")
import os
from dotenv import load_dotenv

load_dotenv()

def load_config():
    return {
        'api_key': os.getenv("OPENAI_API_KEY")
    }
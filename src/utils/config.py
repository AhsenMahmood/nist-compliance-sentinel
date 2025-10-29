import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
    GITHUB_REPO = os.getenv("GITHUB_REPO", "AhsenMahmood/nist-compliance-sentinel")
    
    MAX_ARTICLES = 10
    MODEL = "gpt-4o-mini"
    
    @classmethod
    def validate(cls):
        if not cls.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY not found in environment")
        if not cls.GITHUB_TOKEN:
            print("Warning: GITHUB_TOKEN not set. GitHub publishing will be skipped.")
        return True
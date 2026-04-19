import os
from dataclasses import dataclass
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

@dataclass
class Config:
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    SERPAPI_KEY: str = os.getenv("SERPAPI_KEY", "")
    MODEL_NAME: str = "llama-3.3-70b-versatile"
    MAX_SCHOLAR_RESULTS: int = 5
    TEMPERATURE: float = 0.2

config = Config()
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.environ.get("API_KEY")
BASE_URL = os.environ.get("BASE_URL")

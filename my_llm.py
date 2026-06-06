from langchain_openai import ChatOpenAI

from config import MODEL_NAME, TEMPERATURE
from env_utils import API_KEY, BASE_URL

llm = ChatOpenAI(
    model=MODEL_NAME,
    api_key=API_KEY,
    base_url=BASE_URL,
    temperature=TEMPERATURE,
    streaming=True,
)

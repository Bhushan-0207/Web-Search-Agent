import os
from dotenv import load_dotenv
from tavily import TavilyClient

load_dotenv()

tavily = TavilyClient(
    api_key=os.getenv("TAVILY_API_KEY")
)

def search_web(query:str):
    result = tavily.search(
        query=query,
        max_results=3
    )
    return result

def calculator(expression:str):
    try:
        result = eval(expression)
        return str(result)
    except Exception:
        return "Invalid calculation"
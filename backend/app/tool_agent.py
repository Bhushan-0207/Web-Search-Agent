from langchain_core.tools import tool
from app.tools import search_web
from app.config import llm

@tool
def calculator(expression: str):

    """
    Perform mathematical calculations.
    """

    try:

        result = eval(expression)

        return str(result)

    except Exception:

        return "Invalid calculation"
    
@tool
def web_search(query: str):

    """
    Search the web for latest information.
    """

    result = search_web(query)

    return str(result)

tools =[calculator,web_search]

llm_with_tools = llm.bind_tools(tools)

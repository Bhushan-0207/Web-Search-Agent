import re
from typing_extensions import TypedDict
from langgraph.graph import StateGraph,END
from langchain_core.prompts import PromptTemplate
from app.config import llm
from app.tools import search_web
from app.tools import calculator

class AgentState(TypedDict):
    question:str
    decision:str
    search_results:str
    answer:str
    tool_output:str

router_prompt = PromptTemplate(
    template= """"
    
You are an AI routing assistant.

Your job is to decide whether
a user question requires:

- web search
OR
- direct LLM knowledge
OR
- calculator

Rules:

Use web search for:
- latest news
- current events
- live information
- recent updates
- trending topics
- today's information

Use calculator for:
- math
- arithmetic
- calculations
- equations

Use direct answer for:
- general programming
- definitions
- explanations
- concepts
- historical stable facts

Return ONLY:

search

OR

calculator

OR

direct


Question:
{question}
    
""",
input_variables=["question"]
)

router_chain = router_prompt | llm

def decide_search(state):
    print("\n----Decide search----")

    question = state["question"]

    result = router_chain.invoke({
        "question" : question
    })

    decision = result.content.strip().lower()
    print("decision: ",decision)

    return{
        "decision":decision
    }

def web_search(state):
    print("\n----Web search----")

    question = state["question"]

    results = search_web(question)

    fromatted_results = ""

    formatted_results = ""
    for result in results["results"]:
        formatted_results += f"""

Title:
{result['title']}

content:
{result['content']}

URL:
{result['url']}

"""
    return{
        "search_results":formatted_results
    }

def direct_answer(state):
    print("\n----Direct Answer---")

    question = state["question"]

    result = llm.invoke(question)

    return{
        "answer":result.content
    }

def calculate(state):
    print("\n----Calculator-----")

    question = state["question"]

    expression = re.sub(

        r"[^0-9+\-*/(). ]",

        "",

        question
    )
    print("Expression",expression)


    result = calculator(expression)
    return{
        "answer":result
    }

def generate_search_answer(state):
    print("\n-----Genarate search answer----")

    question = state["question"]
    search_results = state["search_results"]

    prompt = f"""

You are a professional AI web search assistant.

Use ONLY the provided search results
to answer the user's question.

Rules:
- Give clear and concise answers
- Do NOT show internal reasoning
- Do NOT guess or assume facts
- Do NOT say things like:
  'I think', 'maybe', 'probably'
- If information is missing,
  clearly say it was not found
- Format answer cleanly


User Question:
{question}


Search Results:
{search_results}

"""

    result = llm.invoke(prompt)

    return{
        "answer": result.content
    }

def route_decision(state):
    decision = state["decision"]

    return decision

builder = StateGraph(AgentState)

builder.add_node("decide_search",decide_search)
builder.add_node("web_search",web_search)
builder.add_node("direct_answer",direct_answer)
builder.add_node("generate_search_answer",generate_search_answer)
builder.add_node("calculate",calculate)

builder.set_entry_point("decide_search")

builder.add_conditional_edges(
    "decide_search",
    route_decision,
    {
        "search":"web_search",
        "direct":"direct_answer",
        "calculator":"calculate"
    }
)

builder.add_edge("web_search","generate_search_answer")
builder.add_edge("generate_search_answer",END)
builder.add_edge("direct_answer",END)
builder.add_edge("calculate",END)

graph = builder.compile()



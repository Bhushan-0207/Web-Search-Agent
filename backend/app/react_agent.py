from typing_extensions import TypedDict
from typing import Annotated
from langgraph.graph import StateGraph,END
from langgraph.graph.message import add_messages
from langchain_core.messages import HumanMessage,ToolMessage,SystemMessage
from app.tool_agent import llm_with_tools,tools

class AgentState(TypedDict):
    messages:Annotated[list,add_messages]                   # conversation history becomes graph state

def assistant(state):
    print("\n-----Assistant-----")

    response = llm_with_tools.invoke([
        SystemMessage(
            content="""
You are a markdown generator.

Rules:
- Output ONLY valid GitHub-flavored Markdown.
- Do NOT wrap the response in quotes.
- Do NOT escape newline characters.
- Do NOT explain markdown.
- Do NOT return JSON.
- Start directly with markdown content.
"""
        )
    ] + state["messages"]
    )

    return{
        "messages":[
            response
        ]
    }

def tool_node(state):

    print("\n--- TOOL NODE ---")


    last_message = state["messages"][-1]


    tool_calls = last_message.tool_calls


    results = []


    for tool_call in tool_calls:

        tool_name = tool_call["name"]

        tool_args = tool_call["args"]


        print("\nTool:", tool_name)

        print("Args:", tool_args)


        for tool in tools:

            if tool.name == tool_name:

                result = tool.invoke(tool_args)

                results.append(
                    ToolMessage(
                        content=str(result),
                        tool_call_id = tool_call["id"]
                    )
                )


    return {

        "messages": results
    }

def should_continue(state):

    last_message = state["messages"][-1]


    if hasattr(last_message, "tool_calls") and last_message.tool_calls:

        return "tools"


    return "end"

builder = StateGraph(AgentState)

builder.add_node("assistant",assistant)
builder.add_node("tools",tool_node)

builder.set_entry_point("assistant")

builder.add_conditional_edges(

    "assistant",

    should_continue,

    {
        "tools": "tools",

        "end": END
    }
)

builder.add_edge("tools","assistant")

graph = builder.compile()


# for i,message in enumerate( response["messages"]):
#     print(f"\n--------Message {i}--------")
#     print(type(message))
#     print(message)


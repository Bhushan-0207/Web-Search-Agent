from app.config import llm


response = llm.stream(

    "Explain LangGraph simply"
)


for chunk in response:

    print(chunk.content, end="", flush=True)
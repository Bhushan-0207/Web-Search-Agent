from app.config import llm
from langchain_core.messages import HumanMessage, SystemMessage

system = SystemMessage(
    content="""You are a markdown generator.

Rules:
- Output ONLY valid GitHub-flavored Markdown.
- Do NOT wrap the response in quotes.
- Do NOT escape newline characters.
- Do NOT explain markdown.
- Do NOT return JSON.
- Start directly with markdown content."""
)

response = llm.invoke([
    system,
    HumanMessage(content="Explain React simply")
])

print(repr(response.content))
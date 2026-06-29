from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from app.tools import search_web
from app.react_agent import graph
from app.config import llm
from langchain_core.messages import HumanMessage,SystemMessage



app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



class chatRequest(BaseModel):
    message:str


@app.get("/")
def home():
    return{
        "return":"backend running!"
    }

@app.post("/chat")
def chat(request: chatRequest):
    result = graph.invoke({
        "messages": [
            HumanMessage(
                content=request.message
            )
        ]
    })
    final_message = result["messages"][-1]
    return {
        "response": final_message.content
    }

def generation_stream(message: str):

    system_message = SystemMessage(
        content="""
You are a helpful AI assistant.

Always respond in proper markdown format.
"""
    )

    try:
        buffer = ""
        for chunk in llm.stream([
            system_message,
            HumanMessage(content=message)
        ]):
            if chunk.content:
                buffer += chunk.content

                if (

                    "\n\n" in buffer or
                    "```" in buffer or
                    len(buffer) > 300
                ):
                    safe_chunk = buffer.replace("\r", "")
                    lines = safe_chunk.split("\n")
                    sse_message = ""
                    for line in lines:
                        sse_message += f"data: {line}\n"
                    sse_message += "\n"
                    yield sse_message
                    buffer = ""

        # remaining text
        if buffer:
            safe_chunk = buffer.replace("\r", "")
            lines = safe_chunk.split("\n")
            sse_message = ""
            for line in lines:
                sse_message += f"data: {line}\n"
            sse_message += "\n"
            yield sse_message

        yield "data: [DONE]\n\n"

    except Exception as e:

        yield f"data: Error: {str(e)}\n\n"

@app.post("/stream")
async def stream_chat(requset: chatRequest):
    return StreamingResponse(
        generation_stream(requset.message),
        media_type="text/event-stream",
        headers={
            "Catch-Control":"no-catch",
            "Connection":"keep-alive"
        }
    )


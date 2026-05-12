from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from app.tools import search_web
from app.react_agent import graph
from app.config import llm
from langchain_core.messages import HumanMessage



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

    from langchain_core.messages import SystemMessage

    system_message = SystemMessage(
        content="""
You are a helpful AI assistant.

Always respond in proper markdown format.

Rules:
- Use headings
- Use bullet points
- Use code blocks
- Use proper spacing
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


                # --------------------------------
                # SEND LARGER STABLE CHUNKS
                # --------------------------------

                if (

                    len(buffer) > 50 or

                    "\n" in buffer or

                    "." in buffer
                ):

                    yield f"data: {buffer}\n\n"

                    buffer = ""


        # send remaining text
        if buffer:

            yield f"data: {buffer}\n\n"


    except Exception as e:

        yield f"data: Error: {str(e)}\n\n"


@app.post("/stream")
async def stream_chat(requset: chatRequest):
    return StreamingResponse(
        generation_stream(requset.message),
        media_type="text/event-stream"
    )


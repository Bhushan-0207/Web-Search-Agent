import requests


response = requests.post(

    "http://127.0.0.1:8000/stream",

    json={

        "message": "Explain LangGraph in short"
    },

    stream=True
)


for chunk in response.iter_content(

    chunk_size=1,

    decode_unicode=True
):

    print(chunk, end="")
import axios from "axios";

const API = axios.create({
    baseURL:"http://127.0.0.1:8000",
});

export const chat = (message) => API.post("/chat",message);

export async function  streamChat(message) {
    const response = await fetch(
        "http://127.0.0.1:8000/stream",
        {
            method : "post",
            headers:{
                "content-Type":"Application/json"
            },
            body: JSON.stringify({message})
        }
    )
    return response
}
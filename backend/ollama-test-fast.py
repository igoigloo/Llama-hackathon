from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import StreamingResponse
import ollama
import asyncio
from typing import AsyncGenerator

app = FastAPI()

@app.websocket("/ws/ollama")
async def ollama_chat(websocket: WebSocket):
    await websocket.accept()
    
    try:
        data = await websocket.receive_json()
        model = data.get("model", "llama2")
        question = data.get("question", "Why is the sky blue?")
        
        stream = ollama.chat(
            model=model,
            messages=[{'role': 'user', 'content': question}],
            stream=True
        )
        
        for chunk in stream:
            content = chunk.get('message', {}).get('content', "")
            if content:
                await websocket.send_text(content)
                await asyncio.sleep(0.01)

    except WebSocketDisconnect:
        print("WebSocket disconnected")
    except Exception as e:
        print("Error:", e)
        await websocket.send_text("An error occurred while processing the request.")
    finally:
        await websocket.close()

@app.post("/chat")
async def chat(request: Request):
    data = await request.json()
    messages = data.get("messages", [])
    
    async def generate_response() -> AsyncGenerator[str, None]:
        stream = ollama.chat(
            model="llama2",
            messages=[{'role': m['role'], 'content': m['content']} for m in messages],
            stream=True
        )
        
        for chunk in stream:
            content = chunk.get('message', {}).get('content', "")
            if content:
                yield f"data: {content}\n\n"
                await asyncio.sleep(0.01)
    
    return StreamingResponse(
        generate_response(),
        media_type='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
        }
    )

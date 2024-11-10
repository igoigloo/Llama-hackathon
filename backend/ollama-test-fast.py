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
        # Receive the initial data (model and question) from the client
        data = await websocket.receive_json()
        model = data.get("model", "llama3.1")
        question = data.get("question", "Why is the sky blue?")
        
        # Start the Ollama chat stream
        stream = ollama.chat(
            model=model,
            messages=[{'role': 'user', 'content': question}],
            stream=True
        )
        
        # Send messages in chunks through the WebSocket
        for chunk in stream:
            content = chunk.get('message', {}).get('content', "")
            if content:  # Only send non-empty content
                await websocket.send_text(content)
                await asyncio.sleep(0.01)  # Control the message streaming speed

    except WebSocketDisconnect:
        print("WebSocket disconnected")
    except Exception as e:
        print("Error:", e)
        await websocket.send_text("An error occurred while processing the request.")
    finally:
        # Ensure the WebSocket is closed after the chat stream completes
        await websocket.close()

@app.post("/chat")
async def chat(request: Request):
    data = await request.json()
    messages = data.get("messages", [])
    
    async def generate_response() -> AsyncGenerator[str, None]:
        stream = ollama.chat(
            model="llama3.1",  # or your preferred model
            messages=[{'role': m['role'], 'content': m['content']} for m in messages],
            stream=True
        )
        
        for chunk in stream:
            content = chunk.get('message', {}).get('content', "")
            if content:
                # Format as SSE (Server-Sent Events)
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

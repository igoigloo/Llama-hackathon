from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import ollama
import asyncio

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

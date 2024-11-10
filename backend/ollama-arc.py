from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from translate import Translator
import ollama
import speech_recognition as sr
from TTS.api import TTS
import tempfile
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TranslationRequest(BaseModel):
    text: str
    target_lang: str = "de"
    use_stt: bool = False
    use_tts: bool = False

@app.post("/api/translate")
async def translate_text(request: TranslationRequest):
    translator = Translator(to_lang=request.target_lang)
    traditional_translation = translator.translate(request.text)
    
    ollama_response = ollama.chat(
        model='llama3.1',
        messages=[{'role': 'user', 'content': f"Translate '{request.text}' to {request.target_lang}"}],
    )
    
    llm_translation = ollama_response['message']['content']
    
    response = {
        "original": request.text,
        "traditional_translation": traditional_translation,
        "llm_translation": llm_translation
    }

    if request.use_tts:
        tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2", gpu=True)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
            tts.tts_to_file(text=llm_translation,
                            file_path=temp_file.name,
                            speaker="Ana Florence",
                            language=request.target_lang,
                            split_sentences=True)
            response["audioUrl"] = f"/audio/{os.path.basename(temp_file.name)}"

    return response

@app.post("/api/speech-to-text")
async def speech_to_text():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        audio = r.listen(source)
    
    try:
        text = r.recognize_google(audio)
        return {"text": text}
    except sr.UnknownValueError:
        return {"error": "Could not understand audio"}
    except sr.RequestError as e:
        return {"error": f"Could not request results; {e}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
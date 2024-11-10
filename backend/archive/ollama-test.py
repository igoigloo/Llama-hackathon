import streamlit as st
from ollama import Client
import os

# Constants
OLLAMA_BASE_URL = os.environ.get("OLLAMA_API", "http://localhost:11434")
MODEL = "llama3.1:8b"
TIMEOUT = 1000
OPTIONS = dict(num_ctx=2048)
ollama = Client(host=OLLAMA_BASE_URL, timeout=TIMEOUT)

# Send prompt to Ollama
def send_prompt(user_input):
    response = ollama.chat(
        model=MODEL, messages=[{"role": "user", "content": user_input}], options=OPTIONS
    )
    return response["message"]["content"]

#streamlit app interface
def chatbot():
    st.title("Chat with Ollama")

    #input box
    user_input = st.text_input("Type your message below:")

    #process input when button is pressed
    if st.button("Send"):
        if user_input:
            response = send_prompt(user_input)
            st.write("🤖 Chatbot:", response)

if __name__ == "__main__":
    chatbot()
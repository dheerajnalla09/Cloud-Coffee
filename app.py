import os
import streamlit as st

# -------------------------------
# 🎨 UI Setup
# -------------------------------
st.set_page_config(page_title="Cloud Coffee ☁️☕")

st.title("☁️ Cloud Coffee Assistant")
st.write("Your mood, your perfect brew ☕")

# -------------------------------
# 📂 File Check
# -------------------------------
file_path = "menu.txt"

if not os.path.exists(file_path):
    st.error("❌ menu.txt not found")
    st.stop()

# -------------------------------
# 🔗 RAG Setup
# -------------------------------
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

@st.cache_resource
def load_db():
    loader = TextLoader(file_path)
    docs = loader.load()
    embeddings = HuggingFaceEmbeddings()
    return FAISS.from_documents(docs, embeddings)

db = load_db()

# -------------------------------
# 🧠 LLM Setup (Lightweight)
# -------------------------------
from transformers import pipeline

@st.cache_resource
def load_llm():
    return pipeline("text-generation", model="gpt2")

llm = load_llm()

# -------------------------------
# 😊 Emotion Detection
# -------------------------------
def detect_emotion(text):
    text = text.lower()

    if "tired" in text:
        return "relaxing coffee"
    elif "happy" in text:
        return "sweet fun coffee"
    elif "sad" in text:
        return "comfort warm coffee"
    elif "hot" in text:
        return "cold refreshing drink"
    else:
        return "coffee"

# -------------------------------
# 🔍 Retrieval
# -------------------------------
def get_context(user_input):
    query = user_input + " " + detect_emotion(user_input)
    docs = db.similarity_search(query, k=2)
    return "\n".join([doc.page_content for doc in docs])

# -------------------------------
# 🤖 LLM Response Generator
# -------------------------------
def generate_response(user_input):
    context = get_context(user_input)

    prompt = f"""
You are a friendly coffee shop assistant.

User mood: {user_input}

Menu:
{context}

Suggest the best drink in a friendly way.
Keep it short.
"""

    result = llm(prompt, max_length=120, num_return_sequences=1)

    return result[0]["generated_text"]

# -------------------------------
# 💬 Chat UI
# -------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_input = st.chat_input("How are you feeling today?")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.markdown(user_input)

    response = generate_response(user_input)

    st.session_state.messages.append({"role": "assistant", "content": response})

    with st.chat_message("assistant"):
        st.markdown(response)
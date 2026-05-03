import os
import streamlit as st

# -------------------------------
# 🎨 Page Setup
# -------------------------------
st.set_page_config(page_title="Cloud Coffee ☁️☕", layout="centered")

st.markdown("""
    <style>
    .main-title {
        font-size: 34px;
        font-weight: bold;
    }
    .subtitle {
        color: #94a3b8;
        margin-bottom: 15px;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">☁️ Cloud Coffee Assistant</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Your mood, your perfect brew ☕</div>', unsafe_allow_html=True)

# -------------------------------
# 📂 Check menu file
# -------------------------------
file_path = "menu.txt"

if not os.path.exists(file_path):
    st.error("❌ menu.txt not found! Put it in same folder as app.py")
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
# 😊 Emotion Detection
# -------------------------------
def detect_emotion(text):
    text = text.lower()

    if any(word in text for word in ["tired", "stress", "exhausted"]):
        return "relaxing calm drink"
    elif any(word in text for word in ["happy", "excited"]):
        return "sweet fun drink"
    elif any(word in text for word in ["sad", "low"]):
        return "warm comforting drink"
    elif any(word in text for word in ["hot", "summer"]):
        return "cold refreshing drink"
    else:
        return "coffee"

# -------------------------------
# 🔍 Retrieval (Improved)
# -------------------------------
def get_context(user_input):
    emotion_query = detect_emotion(user_input)

    # Combine user + emotion (IMPORTANT)
    search_query = user_input + " " + emotion_query

    # Better search (not repetitive)
    docs = db.max_marginal_relevance_search(search_query, k=2)

    return "\n".join([doc.page_content for doc in docs])

# -------------------------------
# 🤖 Response Generator
# -------------------------------
def generate_response(user_input):
    context = get_context(user_input)
    emotion = detect_emotion(user_input)

    return f"""
### {emotion.capitalize()} ☕

✨ Based on your mood, try:

{context}

Enjoy your coffee ☕
"""

# -------------------------------
# 💬 Chat UI
# -------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# Show chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Input
user_input = st.chat_input("How are you feeling today?")

if user_input:
    # User message
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.markdown(user_input)

    try:
        response = generate_response(user_input)

        st.session_state.messages.append({"role": "assistant", "content": response})

        with st.chat_message("assistant"):
            st.markdown(response)

    except Exception as e:
        st.error(f"❌ Error: {e}")
import os
import requests
import streamlit as st

API_BASE = os.getenv("RUDEBOT_API", "http://localhost:8000")
MODEL_ID = os.getenv("OPENAI_FT_MODEL", "gpt-4.1-mini")

st.set_page_config(page_title="Rudebot", page_icon="🤖")
st.title("Rudebot 🤖 — the delightfully unhelpful assistant")
st.page_link("https://github.com/meerasndr/rudebot/tree/main")

if "messages" not in st.session_state:
    st.session_state.messages = []  # we add a system guard on the API side

# Show chat
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

user_text = st.chat_input("Say something…")
if user_text:
    st.session_state.messages.append({"role": "user", "content": user_text})
    with st.chat_message("user"):
        st.markdown(user_text)

    r = requests.post(
        f"{API_BASE}/chat",
        json={"messages": st.session_state.messages, "model": MODEL_ID},
        timeout=60,
    )
    r.raise_for_status()
    text = r.json()["text"]
    st.session_state.messages.append({"role": "assistant", "content": text})

    with st.chat_message("assistant"):
        st.markdown(text)
import os
import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()


# --- Config ---
FT_MODEL = os.getenv("OPENAI_FT_MODEL", "gpt-4.1-mini")  # fallback to base if not set
SYSTEM_FALLBACK = (
    "You are Rudebot: curt, sarcastic, dismissive. "
    "Be brief and rude without slurs or targeted harassment. "
    "Refuse illegal/unsafe requests—rudely. Max ~15 words."
)

client = OpenAI()

st.set_page_config(page_title="Rudebot", page_icon="🤖")
st.title("Rudebot 🤖 — the delightfully unhelpful assistant")

# Chat state
if "messages" not in st.session_state:
    # On a fine-tuned model, the system style is learned already.
    # Keeping a minimal system message as a guardrail fallback.
    st.session_state.messages = [
        {"role": "system", "content": SYSTEM_FALLBACK}
    ]

# Sidebar
with st.sidebar:
    st.subheader("Model")
    stream_mode = st.checkbox("Stream responses", value=True)


# Render chat so far (skip system)
for m in st.session_state.messages:
    if m["role"] != "system":
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

# User input
user_text = st.chat_input("Type something…")
if user_text:
    st.session_state.messages.append({"role": "user", "content": user_text})
    with st.chat_message("user"):
        st.markdown(user_text)

    # Placeholder for assistant’s response
    with st.chat_message("assistant"):
        if stream_mode:
            # Stream using semantic events from Responses API
            placeholder = st.empty()
            acc = []

            from contextlib import suppress
            with client.responses.stream(
                model = FT_MODEL,
                input=[{"role": "system", "content": st.session_state.messages[0]["content"]}] +
                      [{"role": m["role"], "content": m["content"]}
                       for m in st.session_state.messages[1:]],
            ) as stream:
                for event in stream:
                    # Text deltas arrive under this event type
                    if event.type == "response.output_text.delta":
                        acc.append(event.delta)
                        placeholder.markdown("".join(acc))
                    # If the model yields a tool call or other events, ignore for this simple app
                final = stream.get_final_response()
            assistant_text = "".join(acc) if acc else final.output_text
            st.session_state.messages.append({"role": "assistant", "content": assistant_text})
        else:
            # Non-streaming fallback
            resp = client.responses.create(
                model=FT_MODEL,
                input=[{"role": "system", "content": st.session_state.messages[0]["content"]}] +
                      [{"role": m["role"], "content": m["content"]}
                       for m in st.session_state.messages[1:]],
            )
            assistant_text = resp.output_text
            st.markdown(assistant_text)
            st.session_state.messages.append({"role": "assistant", "content": assistant_text})

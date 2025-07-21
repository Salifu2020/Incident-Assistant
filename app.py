import os
os.environ["PYTORCH_NO_LIBRARY_FALLBACK"] = "1"
import streamlit as st
from ingest import DocumentProcessor
from query import KnowledgeAssistant

st.set_page_config(page_title="Knowledge Chatbot", page_icon="📚")
st.title("Incident Assistant")

# --- Load assistant ---
@st.cache_resource
def load_components():
    processor = DocumentProcessor()
    assistant = KnowledgeAssistant(processor, model_name="mistral")
    return assistant

assistant = load_components()

# --- Initialize session state ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
    assistant.reset_history()

MAX_HISTORY = 20

# --- Ask question form ---
with st.form(key="query_form", clear_on_submit=True):
    query = st.text_input("Ask a question:", placeholder="e.g., When is billing notice sent to students?")
    submitted = st.form_submit_button("🔍 Ask")

if submitted:
    if query.strip():
        with st.spinner("🔎 Generating response..."):
            try:
                response = assistant.ask_question(query)
            except Exception as e:
                response = f"❌ Error: {e}"

        # Store interaction
        st.session_state.chat_history.append((query.strip(), response.strip()))
        if len(st.session_state.chat_history) > MAX_HISTORY:
            st.session_state.chat_history = st.session_state.chat_history[-MAX_HISTORY:]
    else:
        st.warning("Please enter a question before submitting.")

# --- Display structured conversation ---
st.markdown("---")
for idx, (user_msg, bot_msg) in enumerate(st.session_state.chat_history, 1):
    st.markdown(f"**🧑‍💼 You {idx}:** {user_msg}")
    st.markdown(f"**🤖 Salibot {idx}:** {bot_msg}")
    st.markdown("")

# --- Reset conversation ---
if st.button("♻️ Reset Conversation"):
    st.session_state.chat_history = []
    assistant.reset_history()
    st.rerun()  # Optional: remove if still causing issues

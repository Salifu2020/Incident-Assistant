# Incident-Assistant

# 🧠 Document-Based Chatbot with Local LLM and ChromaDB

A fast, privacy-friendly AI assistant that answers user questions based on the content of uploaded documents (e.g., PDFs), using local models and vector search.

Built with:
- 🧾 Local PDF ingestion and chunking (PyMuPDF)
- 🔍 Embedding with Hugging Face models (`sentence-transformers`)
- 🧬 Vector storage using ChromaDB + `pgvector` (optional)
- 💬 Mistral-7B via Ollama for local LLM responses
- 🖥️ Streamlit interface + CLI fallback

---

## 📦 Features

✅ Extracts and chunks text from uploaded PDF files  
✅ Generates vector embeddings using Hugging Face (`all-MiniLM-L6-v2`)  
✅ Stores and retrieves document chunks from ChromaDB  
✅ Uses Mistral (via [Ollama](https://ollama.com)) for accurate, grounded answers  
✅ Supports follow-up questions with conversational memory  
✅ Modular design for easy integration with other LLMs or UIs

---

## 🚀 How It Works

1. **Ingest**  
   Parses PDF files into clean text, chunks them, and stores them as vectors in ChromaDB.

2. **Query**  
   Accepts user questions, retrieves relevant chunks using semantic similarity, and passes the result into Mistral (Ollama) to generate a final answer.

3. **Conversational Memory**  
   Maintains dialogue history to support follow-up questions.

---

## 🛠️ Installation

1. **Clone the repo**

```bash
git clone https://github.com/Salifu2020/Incident-Assistant
cd Incident-Assistant

import os
import sys
import fitz  # PyMuPDF
import chromadb
from chromadb.utils import embedding_functions
import hashlib


class DocumentProcessor:
    def __init__(self, persist_directory=".chromadb/"):
        self.client = chromadb.PersistentClient(path=persist_directory)
        self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )

        try:
            self.collection = self.client.get_collection(name="knowledge_base")
            print("📂 Loaded existing 'knowledge_base' collection.")
        except:
            self.collection = self.client.get_or_create_collection(
                name="knowledge_base",
                embedding_function=self.embedding_function
            )
            print("🆕 Created new 'knowledge_base' collection.")

    def extract_text_from_pdf(self, file_path):
        try:
            doc = fitz.open(file_path)
            text = ""
            for page in doc:
                text += page.get_text("text", flags=fitz.TEXT_PRESERVE_WHITESPACE)
            return text
        except Exception as e:
            print(f"❌ Error reading {file_path}: {e}")
            return ""

    def chunk_text(self, text, chunk_size=1000, overlap=200):
        chunks = []
        start = 0
        while start < len(text):
            end = min(start + chunk_size, len(text))
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            start += (chunk_size - overlap)
        return chunks

    def hash_chunk(self, chunk_text):
        return hashlib.md5(chunk_text.encode('utf-8')).hexdigest()

    def process_document(self, file_path):
        doc_name = os.path.basename(file_path)
        text = self.extract_text_from_pdf(file_path)

        if not text.strip():
            print(f"⚠️ No readable text found in {doc_name}. Skipping.")
            return

        chunks = self.chunk_text(text)
        if not chunks:
            print(f"⚠️ No valid chunks extracted from {doc_name}. Skipping.")
            return

        ids = [self.hash_chunk(chunk) for chunk in chunks]

        # Filter out existing IDs to avoid duplicates
        try:
            existing = set(self.collection.get(ids=ids)["ids"])
        except Exception as e:
            print(f"❌ Error fetching existing IDs: {e}")
            existing = set()

        new_chunks = [(chunk, id_) for chunk, id_ in zip(chunks, ids) if id_ not in existing]

        if not new_chunks:
            print(f"ℹ️ All chunks from {doc_name} already exist. Skipping.")
            return

        documents = [chunk for chunk, _ in new_chunks]
        new_ids = [id_ for _, id_ in new_chunks]
        metadatas = [{"source": doc_name} for _ in new_chunks]

        if not (len(documents) == len(new_ids) == len(metadatas)):
            print(f"❌ Skipped {doc_name} due to mismatch in data sizes.")
            return

        try:
            self.collection.add(
                documents=documents,
                ids=new_ids,
                metadatas=metadatas
            )
            print(f"✅ Added {len(new_chunks)} new chunks from {doc_name}")
        except Exception as e:
            print(f"❌ Failed to add chunks for {doc_name}: {e}")

    def process_directory(self, directory_path):
        if not os.path.exists(directory_path):
            raise FileNotFoundError(f"❌ Directory not found: {directory_path}")

        pdf_files = [f for f in os.listdir(directory_path) if f.lower().endswith(".pdf")]
        if not pdf_files:
            print("ℹ️ No PDF files found in the directory.")
            return

        for filename in pdf_files:
            file_path = os.path.join(directory_path, filename)
            print(f"\n📄 Processing: {filename}")
            self.process_document(file_path)


if __name__ == "__main__":
    directory = sys.argv[1] if len(sys.argv) > 1 else "pdfs"
    processor = DocumentProcessor()
    processor.process_directory(directory)


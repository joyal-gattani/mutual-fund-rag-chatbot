import json
from pathlib import Path

import chromadb
from langchain_huggingface import HuggingFaceEmbeddings


BASE_DIR = Path(__file__).resolve().parent.parent
CHROMA_PATH = BASE_DIR / "chroma_db"
CHUNKS_PATH = BASE_DIR / "data" / "processed" / "chunks.json"

COLLECTION_NAME = "hdfc_mutual_funds"


def initialize_database():
    client = chromadb.PersistentClient(path=str(CHROMA_PATH))

    try:
        collection = client.get_collection(name=COLLECTION_NAME)
        print(f"Collection already exists: {COLLECTION_NAME}")
        print(f"Documents: {collection.count()}")
        return collection

    except Exception:
        print("Collection not found. Creating ChromaDB...")

    with open(CHUNKS_PATH, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    print(f"Loaded {len(chunks)} chunks.")

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    collection = client.create_collection(name=COLLECTION_NAME)

    batch_size = 100

    for start in range(0, len(chunks), batch_size):
        batch = chunks[start:start + batch_size]

        texts = [item["text"] for item in batch]
        ids = [f"chunk_{start + i}" for i in range(len(batch))]
        metadatas = [item["metadata"] for item in batch]

        vectors = embeddings.embed_documents(texts)

        collection.add(
            ids=ids,
            documents=texts,
            embeddings=vectors,
            metadatas=metadatas,
        )

        print(f"Added {min(start + batch_size, len(chunks))}/{len(chunks)}")

    print(f"Database ready: {collection.count()} documents")

    return collection
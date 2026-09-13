import json
from pathlib import Path

import chromadb
from langchain_huggingface import HuggingFaceEmbeddings


BASE_DIR = Path(__file__).resolve().parent.parent
CHUNKS_PATH = BASE_DIR / "data" / "processed" / "chunks.json"

COLLECTION_NAME = "hdfc_mutual_funds"


def initialize_database():

    print("Creating in-memory ChromaDB...")

    # No persistent SQLite/database files
    client = chromadb.EphemeralClient()

    collection = client.create_collection(
        name=COLLECTION_NAME
    )

    with open(
        CHUNKS_PATH,
        "r",
        encoding="utf-8"
    ) as f:
        chunks = json.load(f)

    print(f"Loaded {len(chunks)} chunks.")

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    batch_size = 100

    for start in range(0, len(chunks), batch_size):

        batch = chunks[start:start + batch_size]

        texts = [
            item["text"]
            for item in batch
        ]

        ids = [
            f"chunk_{start + i}"
            for i in range(len(batch))
        ]

        metadatas = [
            item["metadata"]
            for item in batch
        ]

        vectors = embeddings.embed_documents(texts)

        collection.add(
            ids=ids,
            documents=texts,
            embeddings=vectors,
            metadatas=metadatas
        )

        print(
            f"Added "
            f"{min(start + batch_size, len(chunks))}"
            f"/{len(chunks)}"
        )

    print(
        f"Database ready: {collection.count()} documents"
    )

    return collection
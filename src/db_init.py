import json
from pathlib import Path

import chromadb
from langchain_huggingface import HuggingFaceEmbeddings


BASE_DIR = Path(__file__).resolve().parent.parent

CHUNKS_PATH = BASE_DIR / "data" / "processed" / "chunks.json"

COLLECTION_NAME = "hdfc_mutual_funds"


def initialize_database():

    print("Starting ChromaDB initialization...")

    # Use in-memory ChromaDB.
    # This avoids Streamlit Cloud persistent-database issues.
    client = chromadb.EphemeralClient()

    print("Creating ChromaDB collection...")

    collection = client.create_collection(
        name=COLLECTION_NAME
    )

    # Check chunks file
    if not CHUNKS_PATH.exists():
        raise FileNotFoundError(
            f"chunks.json not found at: {CHUNKS_PATH}"
        )

    # Load chunks
    with open(
        CHUNKS_PATH,
        "r",
        encoding="utf-8"
    ) as f:
        chunks = json.load(f)

    print(
        f"Loaded {len(chunks)} chunks."
    )

    # Load embedding model
    print("Loading embedding model...")

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    print("Embedding model loaded.")

    batch_size = 100

    for start in range(
        0,
        len(chunks),
        batch_size
    ):

        batch = chunks[
            start:start + batch_size
        ]

        # Text
        texts = [
            item.get("text", "")
            for item in batch
        ]

        # IDs
        ids = [
            f"chunk_{start + i}"
            for i in range(len(batch))
        ]

        # Metadata
        # chunks.json stores metadata as top-level fields.
        metadatas = []

        for item in batch:

            clean_metadata = {
                "fund": str(
                    item.get("fund", "")
                ),
                "document_type": str(
                    item.get("document_type", "")
                ),
                "document_name": str(
                    item.get("document_name", "")
                ),
                "page": str(
                    item.get("page", "")
                ),
                "chunk_number": str(
                    item.get("chunk_number", "")
                ),
            }

            metadatas.append(
                clean_metadata
            )

        # Generate embeddings
        vectors = embeddings.embed_documents(
            texts
        )

        # Add to Chroma
        collection.add(
            ids=ids,
            documents=texts,
            embeddings=vectors,
            metadatas=metadatas
        )

        completed = min(
            start + batch_size,
            len(chunks)
        )

        print(
            f"Added {completed}/{len(chunks)} chunks."
        )

    print(
        f"Database ready: "
        f"{collection.count()} documents."
    )

    return collection
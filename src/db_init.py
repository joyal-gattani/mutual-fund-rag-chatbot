import json
import shutil
from pathlib import Path

import chromadb
from langchain_huggingface import HuggingFaceEmbeddings


BASE_DIR = Path(__file__).resolve().parent.parent
CHROMA_PATH = BASE_DIR / "chroma_db"
CHUNKS_PATH = BASE_DIR / "data" / "processed" / "chunks.json"

COLLECTION_NAME = "hdfc_mutual_funds"


def initialize_database():

    # First try existing database
    if CHROMA_PATH.exists():

        try:
            client = chromadb.PersistentClient(
                path=str(CHROMA_PATH)
            )

            collection = client.get_collection(
                name=COLLECTION_NAME
            )

            print(
                f"Existing collection found: "
                f"{COLLECTION_NAME}"
            )

            print(
                f"Documents: {collection.count()}"
            )

            return collection

        except Exception:
            print(
                "Existing ChromaDB is invalid or incompatible."
            )
            print("Removing old database...")

            shutil.rmtree(
                CHROMA_PATH,
                ignore_errors=True
            )

    # Create a completely fresh database
    CHROMA_PATH.mkdir(
        parents=True,
        exist_ok=True
    )

    client = chromadb.PersistentClient(
        path=str(CHROMA_PATH)
    )

    print("Creating fresh ChromaDB...")

    with open(
        CHUNKS_PATH,
        "r",
        encoding="utf-8"
    ) as f:
        chunks = json.load(f)

    print(
        f"Loaded {len(chunks)} chunks."
    )

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    collection = client.create_collection(
        name=COLLECTION_NAME
    )

    batch_size = 100

    for start in range(
        0,
        len(chunks),
        batch_size
    ):

        batch = chunks[
            start:start + batch_size
        ]

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

        vectors = embeddings.embed_documents(
            texts
        )

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
        f"Database ready: "
        f"{collection.count()} documents"
    )

    return collection
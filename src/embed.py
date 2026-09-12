import json
from pathlib import Path

import chromadb
from chromadb.utils import embedding_functions


# Project paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent

INPUT_FILE = PROJECT_ROOT / "data" / "processed" / "chunks.json"
CHROMA_DIR = PROJECT_ROOT / "chroma_db"


def main():

    # -----------------------------
    # 1. Load chunks
    # -----------------------------

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    print(f"Loaded {len(chunks)} chunks.")


    # -----------------------------
    # 2. Create embedding model
    # -----------------------------

    print("\nLoading embedding model...")

    embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )

    print("Embedding model loaded.")


    # -----------------------------
    # 3. Create ChromaDB
    # -----------------------------

    client = chromadb.PersistentClient(
        path=str(CHROMA_DIR)
    )

    collection = client.get_or_create_collection(
        name="hdfc_mutual_funds",
        embedding_function=embedding_function
    )


    # -----------------------------
    # 4. Prepare data
    # -----------------------------

    ids = []
    documents = []
    metadatas = []

    for chunk in chunks:

        ids.append(str(chunk["chunk_id"]))

        documents.append(chunk["text"])

        metadatas.append({
            "fund": chunk["fund"],
            "document_type": chunk["document_type"],
            "document_name": chunk["document_name"],
            "page": chunk["page"],
            "chunk_number": chunk["chunk_number"]
        })


    # -----------------------------
    # 5. Add chunks to ChromaDB
    # -----------------------------

    print("\nCreating embeddings and storing vectors...")

    batch_size = 100

    for i in range(0, len(documents), batch_size):

        batch_documents = documents[i:i + batch_size]
        batch_ids = ids[i:i + batch_size]
        batch_metadatas = metadatas[i:i + batch_size]

        collection.upsert(
            ids=batch_ids,
            documents=batch_documents,
            metadatas=batch_metadatas
        )

        print(
            f"Processed {min(i + batch_size, len(documents))}/{len(documents)}"
        )


    print("\n" + "=" * 50)
    print("EMBEDDING + VECTOR DATABASE COMPLETE")
    print("=" * 50)

    print(f"Chunks stored: {collection.count()}")
    print(f"Database: {CHROMA_DIR}")


if __name__ == "__main__":
    main()
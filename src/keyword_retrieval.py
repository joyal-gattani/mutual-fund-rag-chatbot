import chromadb
from pathlib import Path


# ============================================================
# CHROMA DATABASE
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

chroma_client = chromadb.PersistentClient(
    path=str(PROJECT_ROOT / "chroma_db")
)

collection = chroma_client.get_collection(
    name="hdfc_mutual_funds"
)


# ============================================================
# KEYWORD SEARCH
# ============================================================

def keyword_search(
    keywords,
    fund=None,
    max_results=10
):
    """
    Search stored Chroma documents using exact keyword matching.

    This is useful for financial metrics and tables where
    semantic retrieval may miss the exact chunk.
    """

    if not keywords:
        return []

    if fund:

        result = collection.get(
            where={"fund": fund}
        )

    else:

        result = collection.get()

    documents = result.get("documents", [])
    metadatas = result.get("metadatas", [])

    print("KEYWORD SEARCH FUND:", fund)
    print("TOTAL FUND CHUNKS:", len(documents))  

    matches = []

    for document, metadata in zip(
        documents,
        metadatas
    ):

        text_lower = document.lower()

        score = 0

        for keyword in keywords:

            if keyword.lower() in text_lower:
                score += 1

        if score > 0:

            matches.append({
                "text": document,
                "metadata": metadata,
                "keyword_score": score
            })

    # Highest keyword match first
    matches.sort(
        key=lambda x: x["keyword_score"],
        reverse=True
    )

    return matches[:max_results]
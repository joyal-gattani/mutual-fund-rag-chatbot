import json
from pathlib import Path

from langchain_text_splitters import RecursiveCharacterTextSplitter


PROJECT_ROOT = Path(__file__).resolve().parent.parent

INPUT_FILE = PROJECT_ROOT / "data" / "processed" / "documents.json"
OUTPUT_FILE = PROJECT_ROOT / "data" / "processed" / "chunks.json"


def main():

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        documents = json.load(f)

    print(f"Loaded {len(documents)} page documents.")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150,
        separators=[
            "\n\n",
            "\n",
            ". ",
            " ",
            ""
        ]
    )

    chunks = []

    for document in documents:

        text = document["text"]

        split_texts = splitter.split_text(text)

        for chunk_number, chunk_text in enumerate(split_texts, start=1):

            chunks.append({
                "chunk_id": len(chunks),
                "fund": document["fund"],
                "document_type": document["document_type"],
                "document_name": document["document_name"],
                "page": document["page"],
                "chunk_number": chunk_number,
                "text": chunk_text
            })

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            chunks,
            f,
            ensure_ascii=False,
            indent=2
        )

    print("\n" + "=" * 50)
    print("CHUNKING COMPLETE")
    print("=" * 50)

    print(f"Page documents: {len(documents)}")
    print(f"Chunks created: {len(chunks)}")
    print(f"Output: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
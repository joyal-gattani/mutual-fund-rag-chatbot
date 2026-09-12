import csv
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_DIR))

from app import retrieve_context

INPUT_FILE = PROJECT_ROOT / "evaluation" / "test_cases.csv"
OUTPUT_FILE = PROJECT_ROOT / "evaluation" / "retrieval_results.csv"


def main():

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        test_cases = list(csv.DictReader(f))

    results = []

    print("=" * 70)
    print("RAG RETRIEVAL EVALUATION - NO GROQ")
    print("=" * 70)
    print(f"Total test cases: {len(test_cases)}")
    print()

    for index, test in enumerate(test_cases, start=1):

        test_id = test["id"]
        question = test["question"]

        print(f"[{index}/50] {test_id}: {question}")

        try:

            contexts = retrieve_context(question, top_k=5)

            sources = []

            for context in contexts:

                metadata = context["metadata"]

                source = (
                    f"{metadata.get('fund')} | "
                    f"{metadata.get('document_name')} | "
                    f"Page {metadata.get('page')}"
                )

                sources.append(source)

            results.append({
                "id": test_id,
                "category": test["category"],
                "question": question,
                "expected_behavior": test["expected_behavior"],
                "retrieved_sources": " || ".join(sources),
                "retrieved_chunks": len(contexts),
                "retrieval_status": "PASS" if contexts else "FAIL",
                "notes": ""
            })

            print(f"    ✓ Retrieved {len(contexts)} chunks")

        except Exception as e:

            print(f"    ✗ ERROR: {e}")

            results.append({
                "id": test_id,
                "category": test["category"],
                "question": question,
                "expected_behavior": test["expected_behavior"],
                "retrieved_sources": "",
                "retrieved_chunks": 0,
                "retrieval_status": "ERROR",
                "notes": str(e)
            })

    fieldnames = [
        "id",
        "category",
        "question",
        "expected_behavior",
        "retrieved_sources",
        "retrieved_chunks",
        "retrieval_status",
        "notes"
    ]

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:

        writer = csv.DictWriter(f, fieldnames=fieldnames)

        writer.writeheader()
        writer.writerows(results)

    print()
    print("=" * 70)
    print("RETRIEVAL EVALUATION COMPLETE")
    print("=" * 70)
    print(f"Results saved to:")
    print(OUTPUT_FILE)


if __name__ == "__main__":
    main()
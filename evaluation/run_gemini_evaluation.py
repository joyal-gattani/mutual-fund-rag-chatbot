import csv
import time
from pathlib import Path

from src.app import retrieve_context, generate_answer


BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = BASE_DIR / "evaluation" / "test_cases.csv"
OUTPUT_FILE = BASE_DIR / "evaluation" / "gemini_results.csv"


def main():

    print("\nStarting Gemini RAG Evaluation...\n")

    with open(
        INPUT_FILE,
        "r",
        encoding="utf-8"
    ) as f:

        reader = csv.DictReader(f)

        test_cases = list(reader)


    results = []


    for index, test in enumerate(test_cases, start=1):

        test_id = test["id"]
        question = test["question"]

        print(
            f"[{index}/{len(test_cases)}] "
            f"{test_id}: {question}"
        )


        try:

            # Retrieve relevant chunks
            contexts = retrieve_context(
                question,
                top_k=8
            )


            # Generate Gemini answer
            answer = generate_answer(
                question,
                contexts
            )


            # Store source information
            sources = []

            for context in contexts:

                metadata = context["metadata"]

                sources.append(
                    f"{metadata.get('fund')} | "
                    f"{metadata.get('document_name')} | "
                    f"Page {metadata.get('page')}"
                )


            results.append(
                {
                    "id": test_id,
                    "category": test["category"],
                    "question": question,
                    "expected_behavior": test[
                        "expected_behavior"
                    ],
                    "actual_answer": answer,
                    "retrieved_sources": " || ".join(
                        sources
                    ),
                    "status": "SUCCESS"
                }
            )


            print("  ✓ Success")


        except Exception as e:

            results.append(
                {
                    "id": test_id,
                    "category": test["category"],
                    "question": question,
                    "expected_behavior": test[
                        "expected_behavior"
                    ],
                    "actual_answer": "",
                    "retrieved_sources": "",
                    "status": f"ERROR: {str(e)}"
                }
            )


            print(
                f"  ✗ Error: {str(e)}"
            )


        # Avoid hitting API limits
        time.sleep(2)


    # ========================================================
    # SAVE RESULTS
    # ========================================================

    fieldnames = [
        "id",
        "category",
        "question",
        "expected_behavior",
        "actual_answer",
        "retrieved_sources",
        "status"
    ]


    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8",
        newline=""
    ) as f:

        writer = csv.DictWriter(
            f,
            fieldnames=fieldnames
        )

        writer.writeheader()

        writer.writerows(results)


    successful = sum(
        1
        for r in results
        if r["status"] == "SUCCESS"
    )


    print("\n" + "=" * 60)

    print("EVALUATION COMPLETE")

    print("=" * 60)

    print(
        f"Total questions: {len(results)}"
    )

    print(
        f"Successful: {successful}"
    )

    print(
        f"Errors: {len(results) - successful}"
    )

    print(
        f"\nResults saved to:\n{OUTPUT_FILE}"
    )


if __name__ == "__main__":
    main()
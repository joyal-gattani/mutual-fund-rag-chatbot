import pandas as pd
import time
from pathlib import Path

from src.app import retrieve_context, generate_answer

BASE_DIR = Path(__file__).resolve().parent

INPUT_FILE = BASE_DIR / "final_gemini_results.csv"
OUTPUT_FILE = BASE_DIR / "final_retry_8.csv"

FAILED_IDS = [
    "T23",
    "T24",
    "T25",
    "T26",
    "T27",
    "T44",
    "T45",
    "T46",
]

df = pd.read_csv(INPUT_FILE)

tests = df[df["id"].isin(FAILED_IDS)].copy()

results = []

print("=" * 60)
print("RETRYING FINAL 8 GEMINI TEST CASES")
print("=" * 60)

for i, (_, row) in enumerate(tests.iterrows(), start=1):

    test_id = row["id"]
    question = row["question"]

    print(f"\n[{i}/8] {test_id}: {question}")

    try:
        contexts = retrieve_context(
            question,
            top_k=8
        )

        answer = generate_answer(
            question,
            contexts
        )

        sources = []

        for context in contexts:
            metadata = context["metadata"]

            sources.append(
                f"{metadata.get('fund')} | "
                f"{metadata.get('document_name')} | "
                f"Page {metadata.get('page')}"
            )

        results.append({
            "id": test_id,
            "category": row["category"],
            "question": question,
            "expected_behavior": row["expected_behavior"],
            "actual_answer": answer,
            "retrieved_sources": " || ".join(sources),
            "status": "SUCCESS"
        })

        print("  ✓ Success")

    except Exception as e:

        results.append({
            "id": test_id,
            "category": row["category"],
            "question": question,
            "expected_behavior": row["expected_behavior"],
            "actual_answer": "",
            "retrieved_sources": "",
            "status": "ERROR"
        })

        print(f"  ✗ Error: {e}")

    # Stay safely below Gemini free-tier request limit
    time.sleep(10)


retry_df = pd.DataFrame(results)

retry_df.to_csv(
    OUTPUT_FILE,
    index=False
)

print("\n" + "=" * 60)
print("RETRY COMPLETE")
print("=" * 60)

print(f"Retried   : {len(retry_df)}")
print(
    f"Successful: "
    f"{(retry_df['status'] == 'SUCCESS').sum()}"
)
print(
    f"Errors    : "
    f"{(retry_df['status'] == 'ERROR').sum()}"
)

print("\nSaved to:")
print(OUTPUT_FILE)
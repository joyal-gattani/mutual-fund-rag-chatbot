import csv
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

INPUT_FILE = PROJECT_ROOT / "evaluation" / "retrieval_results.csv"
OUTPUT_FILE = PROJECT_ROOT / "evaluation" / "retrieval_scored.csv"


def main():

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    for row in rows:

        sources = row["retrieved_sources"].lower()
        question = row["question"].lower()

        score = 0
        notes = []

        # Fund detection
        fund_names = [
            "hdfc mid cap fund",
            "hdfc small cap fund",
            "hdfc flexi cap fund",
            "hdfc large & mid cap fund",
            "hdfc balanced advantage fund"
        ]

        mentioned_funds = [
            fund for fund in fund_names if fund in question
        ]

        if mentioned_funds:
            found_funds = [
                fund for fund in fund_names if fund in sources
            ]

            if all(fund in found_funds for fund in mentioned_funds):
                score += 1
            else:
                notes.append("Missing expected fund in retrieved sources")

        # Basic retrieval existence
        if int(row["retrieved_chunks"]) > 0:
            score += 1
        else:
            notes.append("No chunks retrieved")

        # Comparison queries should retrieve both funds
        if "compare" in question or "difference" in question or "between" in question:

            if len(mentioned_funds) >= 2:
                found_count = sum(
                    fund in sources for fund in mentioned_funds
                )

                if found_count == len(mentioned_funds):
                    score += 1
                else:
                    notes.append("Comparison missing one or more funds")

        if score >= 2:
            row["retrieval_score"] = "PASS"
        else:
            row["retrieval_score"] = "FAIL"

        row["retrieval_notes"] = "; ".join(notes)

    fieldnames = list(rows[0].keys())

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    passed = sum(row["retrieval_score"] == "PASS" for row in rows)
    total = len(rows)

    print("=" * 70)
    print("RETRIEVAL SCORING COMPLETE")
    print("=" * 70)
    print(f"Total:  {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    print(f"Pass Rate: {passed / total * 100:.1f}%")
    print()
    print(f"Saved to:")
    print(OUTPUT_FILE)


if __name__ == "__main__":
    main()
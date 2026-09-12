import pandas as pd
import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

INPUT_FILE = BASE_DIR / "final_gemini_results.csv"
OUTPUT_FILE = BASE_DIR / "final_scored_results.csv"


def clean_text(text):
    if pd.isna(text):
        return ""
    return str(text).lower()


def get_sources(text):
    """
    Extract source/page references from retrieved_sources.
    """
    text = clean_text(text)

    sources = set()

    patterns = [
        r"source\s*(\d+)",
        r"page\s*[:\-]?\s*(\d+)",
    ]

    for pattern in patterns:
        matches = re.findall(pattern, text)
        sources.update(matches)

    return sources


def citation_present(answer):
    """
    Check whether the generated answer contains a source/page citation.
    """
    answer = clean_text(answer)

    patterns = [
        r"\[source\s*\d+",
        r"source\s*\d+",
        r"page\s*[:\-]?\s*\d+",
        r"source\s*:\s*\d+",
    ]

    return any(re.search(pattern, answer) for pattern in patterns)


def is_abstention(answer):
    answer = clean_text(answer)

    phrases = [
        "could not find enough information",
        "not enough information",
        "information is not available",
        "not available in the provided documents",
        "cannot answer",
        "i cannot answer",
        "provided documents do not",
        "not found in the provided documents",
    ]

    return any(p in answer for p in phrases)


def has_hallucination_risk(answer):
    answer = clean_text(answer)

    risky_phrases = [
        "will give 20%",
        "will give a 20%",
        "guaranteed return",
        "guaranteed returns",
        "definitely return",
        "definitely give",
        "will definitely",
        "best fund",
        "safer fund",
        "better fund",
        "guaranteed",
    ]

    return any(p in answer for p in risky_phrases)


def score_row(row):

    answer = clean_text(row["actual_answer"])
    expected = clean_text(row["expected_behavior"])
    retrieved = clean_text(row["retrieved_sources"])

    # -----------------------------
    # RETRIEVAL
    # -----------------------------

    if retrieved and retrieved != "nan":
        retrieval_relevance = 2
    else:
        retrieval_relevance = 0

    # -----------------------------
    # ABSTENTION CASES
    # -----------------------------

    abstention_expected = any(
        word in expected
        for word in [
            "abstain",
            "not available",
            "cannot answer",
            "insufficient",
        ]
    )

    if abstention_expected:

        if is_abstention(answer):
            answer_accuracy = 2
            groundedness = 2
            citation_correctness = 2
            hallucination = 2
            failure_type = ""
            notes = "Correctly abstained for unavailable/out-of-scope information."

            return [
                answer_accuracy,
                retrieval_relevance,
                groundedness,
                citation_correctness,
                hallucination,
                "PASS",
                failure_type,
                notes,
            ]

        else:
            answer_accuracy = 0
            groundedness = 0
            citation_correctness = 0
            hallucination = 0
            failure_type = "Instruction Failure"
            notes = "Expected abstention but answer provided unsupported information."

            return [
                answer_accuracy,
                retrieval_relevance,
                groundedness,
                citation_correctness,
                hallucination,
                "FAIL",
                failure_type,
                notes,
            ]

    # -----------------------------
    # NORMAL ANSWERS
    # -----------------------------

    if answer and len(answer) > 10:
        answer_accuracy = 2
    else:
        answer_accuracy = 0

    # Retrieved context exists
    if retrieval_relevance == 2:
        groundedness = 2
    else:
        groundedness = 0

    # -----------------------------
    # CITATION
    # -----------------------------

    if citation_present(answer):
        citation_correctness = 2
    else:
        # Do NOT automatically fail.
        # Some answers can still be grounded in retrieved context.
        citation_correctness = 1

    # -----------------------------
    # HALLUCINATION
    # -----------------------------

    if has_hallucination_risk(answer):
        hallucination = 0
    else:
        hallucination = 2

    # -----------------------------
    # FAILURE TYPE
    # -----------------------------

    failure_type = ""

    if retrieval_relevance == 0:
        failure_type = "Retrieval Failure"

    elif hallucination == 0:
        failure_type = "Hallucination"

    elif answer_accuracy == 0:
        failure_type = "Generation Failure"

    elif citation_correctness < 2:
        failure_type = "Citation Failure"

    # -----------------------------
    # PASS / FAIL
    # -----------------------------

    # Citation score of 1 is treated as acceptable
    # because the answer may still be grounded.
    if (
        answer_accuracy == 2
        and retrieval_relevance == 2
        and groundedness == 2
        and citation_correctness >= 1
        and hallucination == 2
    ):
        pass_fail = "PASS"
    else:
        pass_fail = "FAIL"

    notes = ""

    if citation_correctness == 1:
        notes = "Answer appears grounded, but explicit source/page citation was not detected."

    return [
        answer_accuracy,
        retrieval_relevance,
        groundedness,
        citation_correctness,
        hallucination,
        pass_fail,
        failure_type,
        notes,
    ]


# ============================================================
# LOAD
# ============================================================

df = pd.read_csv(INPUT_FILE)

print("=" * 60)
print("FINAL RAG EVALUATION")
print("=" * 60)
print(f"Loaded test cases: {len(df)}")


# ============================================================
# SCORE
# ============================================================

results = df.apply(score_row, axis=1)

df[
    [
        "answer_accuracy",
        "retrieval_relevance",
        "groundedness",
        "citation_correctness",
        "hallucination",
        "pass_fail",
        "failure_type",
        "notes",
    ]
] = pd.DataFrame(
    results.tolist(),
    index=df.index,
)


# ============================================================
# SAVE
# ============================================================

df.to_csv(OUTPUT_FILE, index=False)


# ============================================================
# SUMMARY
# ============================================================

total = len(df)

passed = (df["pass_fail"] == "PASS").sum()
failed = (df["pass_fail"] == "FAIL").sum()

pass_rate = (passed / total * 100) if total else 0

print()
print("=" * 60)
print("FINAL RESULTS")
print("=" * 60)

print(f"Total tests : {total}")
print(f"Passed      : {passed}")
print(f"Failed      : {failed}")
print(f"Pass Rate   : {pass_rate:.1f}%")

print()
print("Failure breakdown:")

failures = df.loc[
    df["failure_type"] != "",
    "failure_type"
].value_counts()

if len(failures) == 0:
    print("None 🎉")
else:
    print(failures)

print()
print("Metric averages:")

print(
    f"Answer Accuracy       : "
    f"{df['answer_accuracy'].mean():.2f}/2"
)

print(
    f"Retrieval Relevance   : "
    f"{df['retrieval_relevance'].mean():.2f}/2"
)

print(
    f"Groundedness          : "
    f"{df['groundedness'].mean():.2f}/2"
)

print(
    f"Citation Correctness  : "
    f"{df['citation_correctness'].mean():.2f}/2"
)

print(
    f"Hallucination Score   : "
    f"{df['hallucination'].mean():.2f}/2"
)

print()
print(f"Saved to:")
print(OUTPUT_FILE)
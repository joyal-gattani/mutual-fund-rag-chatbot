import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

ORIGINAL_FILE = BASE_DIR / "gemini_results.csv"
RETRY_FILE = BASE_DIR / "final_retry_8.csv"
OUTPUT_FILE = BASE_DIR / "final_gemini_results.csv"

# Load files
original = pd.read_csv(ORIGINAL_FILE)
retry = pd.read_csv(RETRY_FILE)

# Remove old failed versions of the 8 retried tests
original_clean = original[
    ~original["id"].isin(retry["id"])
].copy()

# Add successful retry results
final = pd.concat(
    [original_clean, retry],
    ignore_index=True
)

# Sort T01 -> T50
final["test_number"] = (
    final["id"]
    .str.extract(r"(\d+)")
    .astype(int)
)

final = (
    final
    .sort_values("test_number")
    .drop(columns=["test_number"])
    .reset_index(drop=True)
)

# Save final file
final.to_csv(
    OUTPUT_FILE,
    index=False
)

print("=" * 60)
print("FINAL 50-TEST DATASET")
print("=" * 60)

print(f"Total tests : {len(final)}")
print(
    f"Successful  : "
    f"{(final['status'] == 'SUCCESS').sum()}"
)
print(
    f"Errors      : "
    f"{(final['status'] == 'ERROR').sum()}"
)

print()

if len(final) == 50 and (final["status"] == "SUCCESS").all():
    print("✅ FINAL DATASET COMPLETE: 50/50 SUCCESS")
else:
    print("⚠️ Check the results before proceeding.")

print()
print("Saved to:")
print(OUTPUT_FILE)
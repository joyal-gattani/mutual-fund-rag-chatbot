from pathlib import Path
import pymupdf
import json


# Project directories
PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


# Convert folder names into readable fund names
FUND_NAMES = {
    "hdfc_flexi_cap": "HDFC Flexi Cap Fund",
    "hdfc_mid_cap": "HDFC Mid Cap Fund",
    "hdfc_large_mid_cap": "HDFC Large & Mid Cap Fund",
    "hdfc_balanced_advantage": "HDFC Balanced Advantage Fund",
    "hdfc_small_cap": "HDFC Small Cap Fund",
    "hdfc_master": "HDFC Mutual Fund"
}


def identify_document_type(filename):
    name = filename.lower()

    if "fund facts" in name or "fund_facts" in name:
        return "Fund Facts"

    if "presentation" in name:
        return "Presentation"

    if "factsheet" in name:
        return "Master Factsheet"

    if "sid" in name:
        return "SID"

    if "kim" in name:
        return "KIM"

    if "leaflet" in name:
        return "Leaflet"

    if "note" in name:
        return "Note"

    return "Other"


def extract_pdf(pdf_path):
    """
    Extract text from every page of a PDF
    and preserve page-level metadata.
    """

    folder_name = pdf_path.parent.name
    fund_name = FUND_NAMES.get(folder_name, folder_name)

    document_type = identify_document_type(pdf_path.name)

    pdf =pymupdf.open(pdf_path)

    documents = []

    for page_number, page in enumerate(pdf, start=1):

        text = page.get_text("text").strip()

        if not text:
            continue

        documents.append({
            "fund": fund_name,
            "document_type": document_type,
            "document_name": pdf_path.name,
            "source_folder": folder_name,
            "page": page_number,
            "text": text
        })

    pdf.close()

    return documents


def main():

    all_documents = []

    pdf_files = list(RAW_DIR.rglob("*.pdf"))

    print(f"\nFound {len(pdf_files)} PDF files.\n")

    for pdf_path in pdf_files:

        print(f"Processing: {pdf_path.name}")

        try:

            documents = extract_pdf(pdf_path)

            all_documents.extend(documents)

            print(
                f"  ✓ Extracted {len(documents)} pages"
            )

        except Exception as e:

            print(
                f"  ✗ ERROR: {e}"
            )

    output_file = PROCESSED_DIR / "documents.json"

    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            all_documents,
            f,
            ensure_ascii=False,
            indent=2
        )

    print("\n" + "=" * 50)
    print("INGESTION COMPLETE")
    print("=" * 50)

    print(f"PDFs processed: {len(pdf_files)}")
    print(f"Pages extracted: {len(all_documents)}")
    print(f"Output: {output_file}")


if __name__ == "__main__":
    main()
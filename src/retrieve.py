from app import retrieve_context


def main():

    query = input("\nEnter your question: ")

    results = retrieve_context(query)

    print("\n" + "=" * 70)
    print("RETRIEVED RESULTS")
    print("=" * 70)

    for i, result in enumerate(results):

        metadata = result["metadata"]

        print(f"\nRESULT {i + 1}")
        print("-" * 70)
        print(f"Fund: {metadata.get('fund')}")
        print(f"Document: {metadata.get('document_name')}")
        print(f"Page: {metadata.get('page')}")
        print(f"\nText:\n{result['text'][:2000]}")


if __name__ == "__main__":
    main()
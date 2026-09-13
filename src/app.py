import os
import re
from pathlib import Path

from dotenv import load_dotenv
from google import genai

from src.keyword_retrieval import keyword_search, collection


# ============================================================
# PATHS / CONFIG
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

MODEL_NAME = "gemini-3.5-flash-lite"


# ============================================================
# LOAD ENVIRONMENT
# ============================================================

load_dotenv(BASE_DIR / ".env")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError(
        "GEMINI_API_KEY not found. Please check your .env file."
    )

client_gemini = genai.Client(
    api_key=GEMINI_API_KEY
)


# ============================================================
# FUND NAMES / ALIASES
# ============================================================

FUND_ALIASES = {
    "HDFC Flexi Cap Fund": [
        "hdfc flexi cap fund",
        "hdfc flexi cap"
    ],

    "HDFC Mid Cap Fund": [
        "hdfc mid cap fund",
        "hdfc mid cap",
        "hdfc mid-cap fund",
        "hdfc mid-cap opportunities fund",
        "hdfc mid cap opportunities fund"
    ],

    "HDFC Large & Mid Cap Fund": [
        "hdfc large & mid cap fund",
        "hdfc large and mid cap fund",
        "hdfc large mid cap fund",
        "hdfc large & mid cap"
    ],

    "HDFC Balanced Advantage Fund": [
        "hdfc balanced advantage fund",
        "hdfc balanced advantage"
    ],

    "HDFC Small Cap Fund": [
        "hdfc small cap fund",
        "hdfc small cap"
    ],
}


# ============================================================
# METRIC DETECTION
# ============================================================

METRIC_ALIASES = {
    "sharpe": [
        "sharpe",
        "sharpe ratio"
    ],

    "beta": [
        "beta"
    ],

    "standard deviation": [
        "standard deviation",
        "std deviation",
        "std. deviation",
        "volatility"
    ],

    "top holdings": [
        "top holdings",
        "top 5 holdings",
        "top 10 holdings",
        "largest holdings",
        "holdings"
    ],

    "top sectors": [
        "top sectors",
        "sector allocation",
        "sector exposure"
    ],

    "aum": [
        "aum",
        "assets under management"
    ],

    "returns": [
        "return",
        "returns",
        "1 year return",
        "3 year return",
        "5 year return",
        "10 year return",
        "since inception"
    ],

    "expense ratio": [
        "expense ratio",
        "ter",
        "total expense ratio"
    ],

    "market cap": [
        "market cap",
        "market-cap",
        "market capitalisation",
        "market capitalization"
    ],
}


# ============================================================
# DETECT FUNDS
# ============================================================

def detect_funds(query):

    query_lower = query.lower()

    detected = []

    for fund, aliases in FUND_ALIASES.items():

        for alias in aliases:

            if alias in query_lower:

                detected.append(fund)
                break

    return detected


# ============================================================
# DETECT METRICS
# ============================================================

def detect_metrics(query):

    query_lower = query.lower()

    detected = []

    for metric, aliases in METRIC_ALIASES.items():

        for alias in aliases:

            if alias in query_lower:

                detected.append(metric)
                break

    return detected


# ============================================================
# FORMAT CHROMA RESULTS
# ============================================================

def format_results(results):

    formatted = []

    if not results:
        return formatted

    documents = results.get("documents", [[]])
    metadatas = results.get("metadatas", [[]])

    if not documents:
        return formatted

    documents = documents[0]
    metadatas = metadatas[0]

    for text, metadata in zip(documents, metadatas):

        formatted.append(
            {
                "text": text,
                "metadata": metadata
            }
        )

    return formatted


# ============================================================
# RETRIEVAL
# ============================================================

def retrieve_context(query, top_k=8):

    detected_funds = detect_funds(query)
    detected_metrics = detect_metrics(query)

    all_results = []


    # --------------------------------------------------------
    # FUND-AWARE SEMANTIC RETRIEVAL
    # --------------------------------------------------------

    if len(detected_funds) >= 2:

        for fund in detected_funds:

            results = collection.query(
                query_texts=[query],
                n_results=top_k,
                where={
                    "fund": fund
                }
            )

            all_results.extend(
                format_results(results)
            )


    elif len(detected_funds) == 1:

        fund = detected_funds[0]

        results = collection.query(
            query_texts=[query],
            n_results=top_k,
            where={
                "fund": fund
            }
        )

        all_results.extend(
            format_results(results)
        )


    else:

        results = collection.query(
            query_texts=[query],
            n_results=top_k
        )

        all_results.extend(
            format_results(results)
        )


    # --------------------------------------------------------
    # KEYWORD RETRIEVAL FOR IMPORTANT METRICS
    # --------------------------------------------------------

    keyword_map = {

        "sharpe": [
            "Sharpe Ratio"
        ],

        "beta": [
            "Beta"
        ],

        "standard deviation": [
            "Standard Deviation"
        ],

        "top holdings": [
            "Top 10 Equity Holdings",
            "Top 10 Holdings"
        ],

        "top sectors": [
            "Sector Allocation",
            "Top Sectors"
        ],

        "aum": [
            "AUM"
        ],

        "returns": [
            "Returns(%)",
            "Returns (%)",
            "Last 3 Years",
            "Last 1 Year"
        ],

        "expense ratio": [
            "Expense Ratio",
            "Total Expense Ratio",
            "TER"
        ],

        "market cap": [
            "Market Cap Segment wise Exposure"
        ],
    }


    for metric in detected_metrics:

        keywords = keyword_map.get(
            metric,
            []
        )

        if detected_funds:

            funds_to_search = detected_funds

        else:

            funds_to_search = [None]


        for fund in funds_to_search:

            keyword_results = keyword_search(
                keywords=keywords,
                fund=fund,
                max_results=10
            )

            all_results.extend(
                keyword_results
            )


    # --------------------------------------------------------
    # REMOVE DUPLICATES
    # --------------------------------------------------------

    unique_results = []

    seen = set()

    for result in all_results:

        metadata = result["metadata"]

        key = (
            metadata.get("fund"),
            metadata.get("document_name"),
            metadata.get("page"),
            metadata.get("chunk_number")
        )

        if key not in seen:

            seen.add(key)

            unique_results.append(
                result
            )


    # --------------------------------------------------------
    # DETERMINISTIC RANKING
    # --------------------------------------------------------

    def ranking_score(result):

        text = result["text"].lower()

        score = 0


        for metric in detected_metrics:

            if (
                metric == "sharpe"
                and "sharpe ratio" in text
            ):
                score += 5000


            elif (
                metric == "beta"
                and "beta" in text
            ):
                score += 1000


            elif (
                metric == "standard deviation"
                and "standard deviation" in text
            ):
                score += 1000


            elif (
                metric == "top holdings"
                and "top 10 equity holdings" in text
            ):
                score += 1000


            elif (
                metric == "top sectors"
                and "sector allocation" in text
            ):
                score += 1000


            elif (
                metric == "aum"
                and "aum" in text
            ):
                score += 500


            elif (
                metric == "returns"
                and (
                    "returns(%)" in text
                    or "returns (%)" in text
                )
            ):
                score += 800


            elif (
                metric == "expense ratio"
                and (
                    "expense ratio" in text
                    or "ter" in text
                )
            ):
                score += 800


            elif (
                metric == "market cap"
                and "market cap" in text
            ):
                score += 800


        # Prefer Fund Facts documents
        if (
            result["metadata"].get(
                "document_type"
            ) == "Fund Facts"
        ):
            score += 100


        # Important quantitative section
        if "quantitative data (risk ratios)" in text:

            score += 500


        # Holdings section
        if "top 10 equity holdings" in text:

            score += 500


        return score


    unique_results.sort(
        key=ranking_score,
        reverse=True
    )


    # --------------------------------------------------------
    # RETURN MORE CHUNKS FOR TABLE QUESTIONS
    # --------------------------------------------------------

    if "top holdings" in detected_metrics:

        return unique_results[:8]


    return unique_results[:3]


# ============================================================
# CLEAN COMPARISON ANSWER
# ============================================================

def clean_comparison_answer(answer):

    # Remove excessive blank lines
    answer = re.sub(
        r"\n{3,}",
        "\n\n",
        answer
    )

    # Remove unwanted citation wording
    answer = re.sub(
        r"Source:\s*\[?Source\s*(\d+)\]?",
        r"[Source \1",
        answer,
        flags=re.IGNORECASE
    )

    return answer.strip()


# ============================================================
# GENERATE ANSWER
# ============================================================

def generate_answer(query, contexts):

    if not contexts:

        return (
            "I could not find enough information "
            "in the provided documents."
        )


    # --------------------------------------------------------
    # BUILD CONTEXT
    # --------------------------------------------------------

    context_blocks = []

    for i, context in enumerate(contexts, start=1):

        metadata = context["metadata"]

        fund = metadata.get(
            "fund",
            "Unknown Fund"
        )

        document = metadata.get(
            "document_name",
            "Unknown Document"
        )

        page = metadata.get(
            "page",
            "Unknown Page"
        )

        text = context["text"]


        block = f"""
[Source {i}]
Fund: {fund}
Document: {document}
Page: {page}

{text}
"""

        context_blocks.append(
            block
        )


    context_text = "\n".join(
        context_blocks
    )


    # --------------------------------------------------------
    # STRICT PROMPT
    # --------------------------------------------------------

    prompt = f"""
You are a source-grounded AI assistant for HDFC Mutual Fund documents.

USER QUESTION:
{query}

PROVIDED CONTEXT:
{context_text}

GROUNDING RULES:

1. Use ONLY information contained in the provided context.

2. Never use outside knowledge.

3. Never invent numbers, dates, holdings, returns, ratios, fund details, or facts.

4. If the context does not contain enough information, say exactly:
"I could not find enough information in the provided documents."

5. Every factual answer MUST include a source citation.

6. Use ONLY this citation format:
[Source X, Page Y]

7. X must correspond to the Source number shown in the context.

8. Y must correspond to the actual page number shown in the context.

9. Never guess or invent source numbers or page numbers.

10. For comparison questions, cite each fund separately.

11. Never mix information between different funds.

12. If two sources contain conflicting values, report the conflicting values and clearly state that the documents show different values.

13. Do not predict future returns.

14. Do not provide personalized investment advice.

15. Do not say that one fund is "better", "safer", "more suitable", "higher growth", or similar unless the provided documents explicitly support that statement.

16. If information is unavailable, abstain instead of guessing.

17. Preserve the terminology used in the source documents.

18. Keep the answer concise and factual.

CITATION REQUIREMENT:

For a single factual answer, use:

"The Sharpe ratio of HDFC Mid Cap Fund is 0.854. [Source 1, Page 1]"

For a comparison, use:

"HDFC Mid Cap Fund: 0.854 [Source 1, Page 1]
HDFC Small Cap Fund: 0.411 [Source 2, Page 1]"

Do NOT write:

Source: ...
Page: ...
(Source 1)
(Page 1)

Always use:

[Source X, Page Y]

IMPORTANT:

Do not cite a source unless that source actually contains the information being stated.

Answer the user's question directly.
"""


    # --------------------------------------------------------
    # GEMINI
    # --------------------------------------------------------

    response = client_gemini.models.generate_content(
        model=MODEL_NAME,
        contents=prompt
    )


    answer = response.text.strip()


    # --------------------------------------------------------
    # CLEAN OUTPUT
    # --------------------------------------------------------

    answer = clean_comparison_answer(
        answer
    )


    return answer


# ============================================================
# TERMINAL TEST
# ============================================================

def main():

    print("=" * 70)
    print("HDFC MUTUAL FUND RAG ASSISTANT")
    print("=" * 70)

    print(
        "\nType 'exit' to stop."
    )


    while True:

        question = input(
            "\nEnter your question: "
        ).strip()


        if question.lower() == "exit":

            break


        if not question:

            continue


        print(
            "\nSearching documents..."
        )


        contexts = retrieve_context(
            question,
            top_k=8
        )


        print(
            f"Retrieved {len(contexts)} relevant chunks."
        )


        print(
            "\nGenerating answer..."
        )


        answer = generate_answer(
            question,
            contexts
        )


        print(
            "\n" + "=" * 70
        )

        print(
            "ANSWER"
        )

        print(
            "=" * 70
        )

        print(
            answer
        )


        print(
            "\n" + "=" * 70
        )


if __name__ == "__main__":

    main()
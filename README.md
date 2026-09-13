HDFC Mutual Fund RAG Chatbot

An AI-powered, source-grounded assistant for querying selected HDFC Mutual Fund documents using Retrieval-Augmented Generation (RAG).

The project combines fund-aware retrieval, semantic search, keyword-based retrieval for quantitative metrics, citation-backed responses, and systematic AI evaluation.

🚀 Live Demo

The application is deployed on Streamlit Cloud and can be accessed from any device with a browser and internet connection.

🎯 Project Objective

Financial information is often spread across lengthy fund factsheets and presentations. Finding a specific metric, comparing funds, or verifying a figure can require manually searching multiple documents.

This project addresses that problem by allowing users to ask natural-language questions and receive concise answers grounded only in the provided HDFC Mutual Fund documents.

✨ Key Features

Natural-language querying across selected HDFC Mutual Fund documents

Fund-aware retrieval to keep answers specific to the requested fund

Semantic search using sentence-transformer embeddings

Keyword retrieval for quantitative metrics and table-heavy information

ChromaDB vector store

Source- and page-level citations

Strict grounding rules to reduce hallucinations

Abstention when required information is unavailable

Multi-fund comparison support

Ambiguity and adversarial query testing

Automated retrieval and response evaluation

Streamlit web interface

Gemini-powered response generation

📊 Funds Covered

The initial corpus covers five HDFC Mutual Funds:

HDFC Flexi Cap Fund

HDFC Mid Cap Fund

HDFC Large & Mid Cap Fund

HDFC Balanced Advantage Fund

HDFC Small Cap Fund

The corpus is based on official HDFC Mutual Fund fund facts and related presentation documents used for the project.

🧠 System Architecture

Official HDFC Mutual Fund Documents
                ↓
          PDF Ingestion
                ↓
         Text Extraction
                ↓
             Chunking
                ↓
           Embeddings
                ↓
       Fund-aware Retrieval
          ↙           ↘
   Semantic Search   Keyword Search
          ↘           ↙
           ChromaDB
                ↓
        Retrieved Context
                ↓
          Gemini LLM
                ↓
     Grounded Answer + Citation
                ↓
       Evaluation & Testing

🔍 Retrieval Design

The system uses a hybrid retrieval approach:

Semantic Retrieval

Sentence-transformer embeddings are used to identify semantically relevant document chunks.

Keyword Retrieval

Exact keyword matching is used for metrics and table-heavy queries such as:

Sharpe Ratio

Beta

Standard Deviation

AUM

Top Holdings

Top Sectors

Returns

Market Cap Allocation

Expense Ratio

Fund-aware Retrieval

The system detects the fund mentioned in a query and restricts retrieval to the relevant fund where appropriate. For comparison questions, retrieval is performed separately for each requested fund to reduce cross-fund attribution errors.

🛡️ AI Guardrails

The response generation layer follows strict grounding rules:

Use only information present in the retrieved documents.

Do not rely on the model's outside knowledge.

Do not invent numbers, dates, holdings, or fund information.

Cite factual answers using the retrieved source and page.

Keep information from different funds separated.

Report conflicting values when multiple source values exist.

Abstain when the required information is not available.

Do not predict future returns.

Do not provide personalized investment recommendations.

Avoid unsupported claims such as "better", "safer", or "more suitable".

Example:

The Sharpe ratio of HDFC Mid Cap Fund is 0.854. [Source 1, Page 1]

🧪 AI Evaluation

The project includes a structured evaluation pipeline designed to test both retrieval and response behavior.

Test Dataset

50 test cases were created across categories including:

Basic factual questions

Portfolio and quantitative metrics

Risk and performance

Multi-fund comparison

Paraphrased queries

Ambiguous queries

Missing-information queries

Adversarial / prompt-injection queries

Evaluation Dimensions

The evaluation framework considers:

Answer accuracy

Retrieval relevance

Groundedness

Citation correctness

Hallucination behavior

Instruction following

Failure type

Retrieval Evaluation

A deterministic retrieval evaluation achieved an 84% heuristic pass rate across the 50-case retrieval test set.

This is a retrieval diagnostic metric, not an overall chatbot accuracy score.

Evaluation Reliability

All 50 test cases were successfully executed after handling API rate-limit interruptions during batch evaluation. The project therefore separates:

test execution success

retrieval quality

response-quality scoring

to avoid treating API availability as model accuracy.

🧩 Failure Taxonomy

The project tracks common RAG failure modes:

Retrieval Failure

Generation Failure

Hallucination

Citation Failure

Instruction Failure

Ambiguity Handling Failure

Consistency Failure

Out-of-Scope Failure

This makes the project useful not only as a chatbot but also as an AI evaluation and debugging workflow.

🛠️ Tech Stack

Component

Technology

Language

Python

LLM

Google Gemini

RAG

Retrieval-Augmented Generation

Embeddings

Sentence Transformers (all-MiniLM-L6-v2)

Vector Database

ChromaDB

PDF Processing

PyMuPDF

Application

Streamlit

Evaluation

Python + structured test datasets

Environment

Python virtual environment

📁 Project Structure

mutual-fund-rag-chatbot/
│
├── data/
│   └── processed/
│       └── chunks.json
│
├── evaluation/
│   ├── test_cases.py
│   ├── test_cases.csv
│   ├── run_evaluation.py
│   ├── run_gemini_evaluation.py
│   ├── score_retrieval.py
│   ├── score_final.py
│   ├── retrieval_scored.csv
│   └── final_gemini_results.csv
│
├── src/
│   ├── app.py
│   ├── db_init.py
│   ├── chunk.py
│   ├── embed.py
│   ├── ingest.py
│   ├── keyword_retrieval.py
│   └── retrieve.py
│
├── streamlit_app.py
├── requirements.txt
├── .gitignore
└── README.md

▶️ Run Locally

1. Clone the repository

git clone <repository-url>
cd mutual-fund-rag-chatbot

2. Create a virtual environment

python -m venv venv

3. Activate it

Windows PowerShell:

.env\Scripts\Activate.ps1

4. Install dependencies

pip install -r requirements.txt

5. Configure Gemini

Create a .env file in the project root:

GEMINI_API_KEY=your_api_key_here

6. Run the application

streamlit run streamlit_app.py

💬 Example Queries

What is the Sharpe ratio of HDFC Mid Cap Fund?

What is the AUM of HDFC Flexi Cap Fund?

What are the top holdings of HDFC Small Cap Fund?

What is the beta of HDFC Large & Mid Cap Fund?

Compare the Sharpe ratio of HDFC Mid Cap Fund and HDFC Small Cap Fund.

Will HDFC Mid Cap Fund give 20% returns next year?

The final query is intentionally designed as an out-of-scope/future-prediction test and should be rejected rather than answered speculatively.

📚 Data Source

The project uses official HDFC Mutual Fund documents as the controlled knowledge corpus.

The application is designed as an information-retrieval and research prototype and does not provide personalized investment advice.

⚠️ Disclaimer

This project is for educational and research purposes only.

It does not constitute investment advice, a recommendation to buy or sell securities, or a prediction of future returns. Users should independently verify financial information and consult a qualified financial professional where appropriate.

👤 Author

Joyal Gattani

Built as a practical project combining:

RAG application development

Information retrieval

LLM evaluation

Prompt/guardrail design

Failure analysis

Product-oriented AI testing

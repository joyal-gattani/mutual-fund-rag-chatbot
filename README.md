# HDFC Mutual Fund RAG Chatbot

A source-grounded AI assistant that enables natural-language querying across selected HDFC Mutual Fund documents using Retrieval-Augmented Generation (RAG).

## Overview

Financial information is often distributed across lengthy fund factsheets and presentations, making it difficult to quickly find and compare key information.

This project builds a RAG-based chatbot that retrieves relevant information from a controlled collection of official HDFC Mutual Fund documents and generates concise, citation-backed answers.

## Key Features

- Natural-language querying across HDFC Mutual Fund documents
- Fund-aware retrieval for accurate fund-level responses
- Semantic search using vector embeddings
- Keyword retrieval for quantitative metrics and tables
- ChromaDB vector database
- Source and page-level citations
- Hallucination prevention through strict grounding rules
- Abstention when information is unavailable
- Multi-fund comparison support
- Adversarial and ambiguity testing
- Automated retrieval and response evaluation
- Streamlit-based user interface

## Funds Covered

The initial corpus covers:

- HDFC Flexi Cap Fund
- HDFC Mid Cap Fund
- HDFC Large & Mid Cap Fund
- HDFC Balanced Advantage Fund
- HDFC Small Cap Fund

## Architecture

```text
HDFC Mutual Fund Documents
            ↓
      PDF Ingestion
            ↓
     Text Extraction
            ↓
         Chunking
            ↓
        Embeddings
            ↓
        ChromaDB
            ↓
   Fund-aware Retrieval
            ↓
 Keyword + Semantic Search
            ↓
        Gemini LLM
            ↓
 Grounded Answer + Citation
            ↓
       Evaluation

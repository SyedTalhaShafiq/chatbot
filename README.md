# DevOps Project (Secure AI Agent)

This repository contains the DevOps Project, a secure, agentic AI system designed to assist users with logistics inquiries. It leverages a **Hybrid RAG (Retrieval-Augmented Generation)** pipeline and an **AI Guardrail** system to ensure accurate and safe responses.

## Key Features

*   **Hybrid RAG Pipeline**: Combines **Vector Search** (semantic understanding) and **BM25** (keyword matching) using a `QueryFusionRetriever` for superior checking of knowledge base coverage.
*   **ReAct Agent Architecture**: Uses a reasoning loop (Thought-Action-Observation) to dynamically select tools and answer complex user queries.
*   **AI Guardrails**: Implements a dedicated `LLMGuard` layer that checks user inputs against safety taxonomies before processing.
*   **FastAPI Backend**: Provides a robust, asynchronous REST API for easy integration with frontend applications.
*   **Vector Database**: Uses **ChromaDB** for efficient storage and retrieval of document embeddings.

## Project Structure

*   **`app.py`**: The main entry point for the FastAPI server. Handles lifecycle management (loading models) and chat endpoints.
*   **`pipeline.py`**: Core logic for assembling the RAG pipeline. Configures the Agent, tools, and Guardrails.
*   **`rag_comp.py`**: Components repository. Manages Embeddings (HuggingFace), LLM (Gemini), and Vector Store (ChromaDB) connections.
*   **`chatbot.py`**: A standalone CLI script for testing the agent in the terminal.
*   **`config.py`**: Configuration management (environment variables, model names, paths).
*   **`cloud_utils.py`**: Utilities for cloud interactions (e.g., downloading the Vector DB from S3).

## Prerequisites

*   Python 3.9+
*   Google Gemini API Key
*   (Optional) AWS Credentials if downloading Vector DB from S3.

## Installation

1.  **Clone the repository** and navigate to the directory.
2.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
3.  **Environment Setup**:
    Create a `.env` file in this directory with the following keys:
    ```env
    GOOGLE_API_KEY=your_gemini_api_key_here
    AWS_ACCESS_KEY_ID=your_aws_key  # If needed
    AWS_SECRET_ACCESS_KEY=your_aws_secret # If needed
    ```

## Usage

### Running the API Server
Start the FastAPI backend with Uvicorn:
```bash
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```
The API will be available at `http://localhost:8000`. 
*   **Swagger UI**: Visit `http://localhost:8000/docs` to test endpoints interactively.

### Running the CLI Chatbot
For quick testing without a server:
```bash
python chatbot.py
```

## Architecture Details

### The Hybrid RAG Engine
The system uses `rag_comp.py` to initialize:
1.  **HuggingFace Embeddings**: For converting text to vectors.
2.  **ChromaDB**: As the vector store.
3.  **BM25 Retriever**: For precise keyword lookup (if raw data is present).
4.  **QueryFusionRetriever**: Merges results from both Vector and BM25 sources using a relative score fusion strategy.

### The Guardrail System
Security is handled by the `LLMGuard` class in `pipeline.py`. It serves as a middleware that acts **before** the agent processes any query, intercepting requests that violate defined safety policies (e.g., jailbreaks, prompt injection).

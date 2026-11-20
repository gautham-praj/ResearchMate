# ResearchMate

**A Local-First AI Research Assistant for PDF Question Answering**

ResearchMate is an AI-powered research assistant that allows users to upload PDF documents, ask questions about their contents, and receive answers grounded in relevant passages from the uploaded documents.

It uses a Retrieval-Augmented Generation (RAG) pipeline with locally running language and embedding models through Ollama. FAISS provides vector similarity search, while FastAPI handles the backend and Next.js provides the user interface.

The core workflow runs locally without requiring paid AI APIs.

## Features

- **PDF Upload:** Upload and validate PDF documents through the web interface.
- **Text Extraction:** Extract document text page by page using PyMuPDF.
- **Intelligent Chunking:** Split extracted text into overlapping chunks while preserving page metadata.
- **Local Embeddings:** Generate text embeddings using Ollama and `nomic-embed-text`.
- **Vector Search:** Store and retrieve document embeddings using FAISS.
- **Document-Scoped Retrieval:** Retrieve relevant passages from the selected document rather than searching unrelated documents.
- **AI-Powered Question Answering:** Generate document-grounded answers using the Qwen 2.5 3B Instruct model.
- **Source References:** Return relevant source passages with their corresponding page numbers.
- **Relevance Filtering:** Filter low-scoring retrieval results using an initial empirically selected similarity threshold.
- **Interactive Frontend:** Upload PDFs, ask questions, read formatted answers, and expand source passages.

## Architecture

```text
                     USER
                       |
                       v
                Next.js Frontend
                       |
                  HTTP Requests
                       |
                       v
                 FastAPI Backend
                       |
              +--------+--------+
              |                 |
              v                 v
        DOCUMENT UPLOAD    DOCUMENT QUESTION
              |                 |
              v                 v
       documents.py       documents.py
              |                 |
              v                 v
      document_service    document_qa_service
              |                 |
              v                 v
         PDF Validation    Question Embedding
              |                 |
              v                 v
         PyMuPDF          Ollama Embeddings
              |           (nomic-embed-text)
              v                 |
        Text Extraction         v
              |            FAISS Search
              v                 |
        Text Chunking           v
              |           Relevance Filtering
              v                 |
       Ollama Embeddings        v
       (nomic-embed-text)  Context Construction
              |                 |
              v                 v
         FAISS Index       Ollama LLM
              |            (Qwen 2.5 3B)
              |                 |
              v                 v
       Vector Index +       Generated Answer
       JSON Metadata        + Source Passages
              |                 |
              v                 v
         Local Storage    FastAPI Response
                                |
                                v
                         Next.js Frontend
```

## Technology Stack

| Component          | Technology                   |
| ------------------ | ---------------------------- |
| Frontend           | Next.js, React, TypeScript   |
| Styling            | Tailwind CSS                 |
| Markdown Rendering | React Markdown, remark-gfm   |
| Backend            | Python, FastAPI              |
| PDF Processing     | PyMuPDF                      |
| Embedding Model    | Ollama, nomic-embed-text     |
| Language Model     | Ollama, Qwen 2.5 3B Instruct |
| Vector Search      | FAISS                        |
| HTTP Client        | HTTPX                        |
| Configuration      | Pydantic Settings            |
| Backend Testing    | Pytest                       |

## How the RAG Pipeline Works

ResearchMate follows a Retrieval-Augmented Generation workflow.

### 1. Document Upload

The user uploads a PDF through the Next.js frontend. The FastAPI backend validates the file and stores it locally.

### 2. Text Extraction

PyMuPDF extracts text from each page of the PDF. Page numbers are retained as metadata for source references.

### 3. Text Chunking

The extracted text is divided into smaller, overlapping chunks.

Each chunk retains metadata such as:

- Page number
- Chunk index
- Extracted text

Overlapping chunks help preserve context between adjacent passages.

### 4. Embedding Generation

The local `nomic-embed-text` model converts each text chunk into a numerical vector representation.

These embeddings capture semantic information that can be used to identify passages relevant to a question.

### 5. Vector Storage

FAISS stores the generated vectors in a document-specific index.

The corresponding chunk metadata is persisted alongside the index.

### 6. Question Processing

When a user asks a question, ResearchMate generates an embedding for that question using the same embedding model.

### 7. Similarity Search

FAISS compares the question embedding with the stored document embeddings and retrieves the most similar passages.

### 8. Relevance Filtering

Retrieved passages are filtered using an initial similarity threshold to reduce the inclusion of unrelated content.

### 9. Context Construction

The relevant passages are combined into a context and included in a prompt alongside the user's question.

### 10. Answer Generation

The local Qwen 2.5 3B Instruct model generates an answer using the supplied document context.

The prompt instructs the model to avoid unsupported claims, ignore instructions contained in document excerpts, and indicate when the document does not contain sufficient information.

### 11. Source References

The backend returns the generated answer together with the retrieved source passages and their page numbers.

The frontend displays the answer and allows users to expand the source passages.

## Project Structure

```text
ResearchMate/
│
├── backend/
│   │
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   │
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   └── routes/
│   │   │       ├── __init__.py
│   │   │       ├── chat.py
│   │   │       └── documents.py
│   │   │
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   └── config.py
│   │   │
│   │   └── services/
│   │       ├── __init__.py
│   │       ├── ollama_service.py
│   │       ├── pdf_service.py
│   │       ├── document_service.py
│   │       ├── chunking_service.py
│   │       ├── embedding_service.py
│   │       ├── vector_store_service.py
│   │       ├── document_ingestion_service.py
│   │       └── document_qa_service.py
│   │
│   ├── tests/
│   │   ├── test_main.py
│   │   ├── test_config.py
│   │   ├── test_pdf_service.py
│   │   ├── test_document_service.py
│   │   ├── test_documents_api.py
│   │   ├── test_chunking_service.py
│   │   ├── test_embedding_service.py
│   │   ├── test_vector_store_service.py
│   │   ├── test_document_ingestion_service.py
│   │   ├── test_document_qa_service.py
│   │   └── test_document_qa_api.py
│   │
│   └── data/
│       ├── documents/
│       └── vector_store/
│
├── frontend/
│   ├── app/
│   │   ├── favicon.ico
│   │   ├── globals.css
│   │   ├── layout.tsx
│   │   └── page.tsx
│   │
│   ├── public/
│   ├── .gitignore
│   ├── AGENTS.md
│   ├── eslint.config.mjs
│   ├── next.config.ts
│   ├── package.json
│   ├── package-lock.json
│   ├── README.md
│   └── tsconfig.json
│
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## Prerequisites

Install the following before running ResearchMate:

- Python 3.12
- Node.js and npm
- Git
- [Ollama](https://ollama.com/)

### Download the required Ollama models

Start Ollama and run:

```powershell
ollama pull qwen2.5:3b-instruct
ollama pull nomic-embed-text
```

The first model is used for answer generation. The second generates embeddings for document passages and user questions.

## Installation and Setup

### 1. Clone the repository

```powershell
git clone https://github.com/gautham-praj/ResearchMate.git
cd ResearchMate
```

Replace the placeholder with your actual repository URL.

### 2. Create and activate a Python virtual environment

From the project root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install backend dependencies

```powershell
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root.

Add the following configuration:

```env
OLLAMA_URL=http://localhost:11434/api/generate
OLLAMA_MODEL=qwen2.5:3b-instruct

OLLAMA_EMBEDDING_URL=http://localhost:11434/api/embed
OLLAMA_EMBEDDING_MODEL=nomic-embed-text
```

The `.env` file is excluded from Git. The repository includes `.env.example` as a configuration reference.

### 5. Start the backend

Open a terminal from the project root:

```powershell
cd backend
..\.venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --reload
```

The backend will be available at:

- API: http://127.0.0.1:8000
- Interactive API documentation: http://127.0.0.1:8000/docs
- Health check: http://127.0.0.1:8000/health

Keep this terminal running.

### 6. Install frontend dependencies

Open a second terminal:

```powershell
cd frontend
npm install
```

### 7. Start the frontend

```powershell
npm run dev
```

Open the application:

http://localhost:3000

Make sure the backend and Ollama are running while using the application.

## API Endpoints

The FastAPI backend currently exposes the following main endpoints:

| Method | Endpoint                       | Purpose                                   |
| ------ | ------------------------------ | ----------------------------------------- |
| GET    | `/`                            | API welcome message                       |
| GET    | `/health`                      | Backend health check                      |
| POST   | `/chat`                        | General LLM chat                          |
| POST   | `/documents/upload`            | Upload and ingest a PDF                   |
| POST   | `/documents/{document_id}/ask` | Ask a question about an uploaded document |

Interactive API documentation is available at:

http://127.0.0.1:8000/docs

## Running Tests

### Backend tests

From the backend directory, with the virtual environment activated:

```powershell
python -m pytest -v
```

The backend test suite has passed with **44 tests** during development.

The tests cover:

- Application and configuration
- PDF validation and text extraction
- Document upload and storage
- Text chunking
- Embedding generation
- FAISS vector storage and retrieval
- Document ingestion
- Document question answering
- API error handling
- Relevance filtering

### Frontend linting

From the frontend directory:

```powershell
npm run lint
```

### Frontend production build

```powershell
npm run build
```

Both frontend checks have passed during development.

## Design Principles

ResearchMate is built around the following principles:

- **Local-first:** Document processing, embeddings, vector search, and language-model inference run locally.
- **Privacy-conscious:** Uploaded documents and vector data are stored locally rather than sent to a paid external AI API.
- **Modular architecture:** PDF processing, chunking, embeddings, vector storage, and question answering are separated into independent services.
- **Document-grounded answers:** Responses are generated using retrieved passages from the selected document.
- **Source transparency:** Retrieved passages and page numbers are returned alongside answers.
- **Testability:** Backend services and API behaviour are covered by automated tests.

## Current Limitations

ResearchMate is an actively developed prototype. The following capabilities are not yet implemented or fully evaluated:

- OCR support for scanned PDFs and image-only documents.
- Direct navigation from a source reference to the corresponding page in an embedded PDF viewer.
- Authentication and multi-user access control.
- Complete document deletion and lifecycle management through the API.
- Advanced retrieval techniques such as reranking and hybrid keyword-vector search.
- Broad evaluation of retrieval quality across different document types and question categories.
- Production deployment and production-level monitoring.

The current similarity threshold is an initial empirical choice based on observed test queries. It is not a universal measure of relevance or answer correctness.

## Future Improvements

Potential next steps include:

- PDF preview with page navigation.
- OCR for scanned documents.
- Improved retrieval using reranking and hybrid search.
- Document management and deletion.
- Conversation history for document-specific questions.
- More extensive retrieval and answer-quality evaluation.
- Deployment and monitoring.

## Project Status

The current prototype supports the core PDF question-answering workflow:

**Upload PDF → Extract Text → Chunk → Embed → Store → Retrieve → Generate Answer → Display Sources**

The backend test suite has passed 44 tests, and the frontend has passed linting and production-build checks.

---

# Enterprise Integration Sales Engineer AI Agent

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.32-red?style=for-the-badge&logo=streamlit)
![LangChain](https://img.shields.io/badge/LangChain-0.2-green?style=for-the-badge)
![Groq](https://img.shields.io/badge/Groq-Llama%203.3%2070B-orange?style=for-the-badge)
![License](https://img.shields.io/badge/License-Proprietary-darkred?style=for-the-badge)

**An AI-powered Sales Engineer Agent that transforms client meeting transcripts into professional, board-ready Solution Design Documents — in under 60 seconds.**

[Architecture](#system-architecture) · [Setup Guide](#local-setup) · [Sample Transcripts](#sample-transcripts)

</div>

---

## What This Does

Upload any client discovery call transcript (`.txt`) → The AI Agent:

1. **Analyzes** the transcript using LLM to extract structured client insights (pain points, tech stack, budget, timeline, decision makers)
2. **Retrieves** the most relevant internal case study from the knowledge base using RAG (FAISS semantic search)
3. **Generates** a complete 11-section Solution Design Document tailored to the client
4. **Delivers** a downloadable `.md` or `.txt` document — ready for stakeholder presentation

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Streamlit Frontend (app.py)                       │
│  ┌─────────────────┐          ┌──────────────────────────────────┐  │
│  │  Upload Panel   │          │      Results Panel               │  │
│  │  (.txt file)    │          │  ┌─────────────┐ ┌────────────┐  │  │
│  │  Preview        │          │  │Client       │ │ Solution   │  │  │
│  │  Generate Btn   │          │  │Analysis Tab │ │ Doc Tab    │  │  │
│  └────────┬────────┘          └──┴─────────────┴─┴────────────┘  │  │
└───────────┼─────────────────────────────────────────────────────────┘
            │ Transcript Text
            ▼
┌─────────────────────────────────────────────────────────────────────┐
│                  Agent Pipeline (3 steps)                            │
│                                                                      │
│  Step 1: TranscriptAnalyzerAgent (agents.py)                        │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │  Input: Raw transcript text                                  │   │
│  │  LLM: Groq / Llama 3.3 70B (via langchain-groq)             │   │
│  │  Prompt: TRANSCRIPT_ANALYZER_PROMPT (prompts.py)             │   │
│  │  Output: Structured JSON {client_name, pain_points,          │   │
│  │          tech_stack, budget_range (₹), timeline, ...}        │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                            │                                         │
│  Step 2: RAGSystem (rag.py)                                         │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │  Embeddings: HuggingFace all-MiniLM-L6-v2 (local, free)     │   │
│  │  Vector Store: FAISS (local index, persisted to disk)        │   │
│  │  Knowledge Base: 7 case studies (case_studies/*.txt)         │   │
│  │  Query: Semantic search based on extracted insights          │   │
│  │  Output: Most relevant case study text                       │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                            │                                         │
│  Step 3: SolutionArchitectAgent (agents.py)                         │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │  Input: JSON insights + retrieved case study                 │   │
│  │  LLM: Groq / Llama 3.3 70B                                  │   │
│  │  Prompt: SOLUTION_ARCHITECT_PROMPT (prompts.py)              │   │
│  │  Output: 11-section Solution Design Document (Markdown)      │   │
│  └──────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘

Knowledge Base (case_studies/)          Sample Transcripts
├── ecommerce.txt  (UrbanCart)          ├── transcript_ecommerce_trendbazaar.txt
├── fintech.txt    (NovaPay)            ├── transcript_fintech_finarc.txt
├── healthcare.txt (MedCore)            ├── transcript_healthcare_medcore.txt
├── logistics.txt  (ShipSmart)          ├── transcript_logistics_fasttrack.txt
├── edtech.txt     (LearnBridge)        ├── transcript_edtech_edupeak.txt
├── manufacturing_erp.txt (PrecisionForge) ├── transcript_manufacturing_bharatauto.txt
└── media_ott.txt  (StreamVista)        └── transcript_media_cinestar.txt
```

---

## Tech Stack

### Backend
| Component | Technology | Purpose |
|---|---|---|
| Language | **Python 3.10+** | Core runtime |
| LLM Framework | **LangChain 0.2** | Agent orchestration, prompt management |
| LLM Provider | **Groq API (Llama 3.3 70B)** | Transcript analysis + document generation |
| Embeddings | **HuggingFace `all-MiniLM-L6-v2`** | Local sentence embeddings (no API cost) |
| Vector Store | **FAISS** | Semantic similarity search over case studies |
| RAG | **LangChain + FAISS + HuggingFace** | Knowledge retrieval pipeline |

### Frontend
| Component | Technology | Purpose |
|---|---|---|
| UI Framework | **Streamlit 1.32** | Full-stack Python web UI |
| Styling | **Custom CSS (Inter font, glassmorphism dark theme)** | Premium UI |
| Deployment | **Streamlit Community Cloud** | Free public deployment |

### Key Libraries
```
langchain==0.2.x          # Agent orchestration and prompt templates
langchain-groq==0.2.4     # Groq LLM integration for LangChain
langchain-community        # FAISS vector store, HuggingFace embeddings, document loaders
groq==0.15.0               # Groq Python SDK
sentence-transformers      # HuggingFace embedding model (runs locally)
faiss-cpu                  # Facebook AI Similarity Search — vector indexing
streamlit==1.32.x          # Web UI framework
```

---

## Project Structure

```
sales_engineer_agent/
├── app.py                  # Main Streamlit application (UI + pipeline orchestration)
├── agents.py               # LangChain agents (TranscriptAnalyzerAgent, SolutionArchitectAgent)
├── rag.py                  # RAGSystem (FAISS index management, retrieval)
├── prompts.py              # All LLM prompt templates (PromptTemplate objects)
├── requirements.txt        # Python dependencies
├── case_studies/           # Knowledge base for RAG
│   ├── ecommerce.txt
│   ├── fintech.txt
│   ├── healthcare.txt
│   ├── logistics.txt
│   ├── edtech.txt
│   ├── manufacturing_erp.txt
│   └── media_ott.txt
├── sample_transcripts/     # Example client transcripts for testing
│   ├── transcript_ecommerce_trendbazaar.txt
│   ├── transcript_fintech_finarc.txt
│   ├── transcript_healthcare_medcore.txt
│   ├── transcript_logistics_fasttrack.txt
│   ├── transcript_edtech_edupeak.txt
│   ├── transcript_manufacturing_bharatauto.txt
│   └── transcript_media_cinestar.txt
├── faiss_index/            # Auto-generated FAISS vector index (gitignored)
├── .streamlit/
│   └── secrets.toml        # API key config (gitignored — never commit this)
├── .gitignore
├── pyrightconfig.json      # VS Code type-checker config
└── README.md
```

---

## Local Setup

### Prerequisites
- Python 3.10 or higher
- A free **Groq API key** — get one at [console.groq.com](https://console.groq.com) (no credit card required)

### Step 1 — Clone the Repository
```bash
git clone https://github.com/YOUR_USERNAME/enterprise-sales-engineer-ai.git
cd enterprise-sales-engineer-ai/sales_engineer_agent
```

### Step 2 — Create and Activate Virtual Environment
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# macOS / Linux
python -m venv venv
source venv/bin/activate
```

### Step 3 — Install Dependencies
```bash
pip install -r requirements.txt
```
> ⚠️ First install downloads the HuggingFace embedding model (~90MB). This is a one-time download.

### Step 4 — Configure API Key
Create the file `.streamlit/secrets.toml`:
```toml
GROQ_API_KEY = "gsk_your_key_here"
```

### Step 5 — Run the App
```bash
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser.

### Step 6 — Test with a Sample Transcript
1. Click **Browse files** and upload any file from `sample_transcripts/`
2. Click **🚀 Generate Solution Design Document**
3. Review the **Client Analysis** and **Solution Document** tabs
4. Download the generated `.md` or `.txt` document

---

## Sample Transcripts

The `sample_transcripts/` folder contains 7 realistic Indian enterprise client discovery call transcripts covering:

| File | Company | Industry | Budget |
|---|---|---|---|
| `transcript_ecommerce_trendbazaar.txt` | TrendBazaar Group | E-Commerce | ₹7.5 Cr – ₹10 Cr |
| `transcript_fintech_finarc.txt` | FinArc Financial | Fintech / Payments | ₹5 Cr – ₹6.5 Cr |
| `transcript_healthcare_medcore.txt` | MedCore Hospitals | Healthcare / HIMS | ₹26.5 Cr |
| `transcript_logistics_fasttrack.txt` | FastTrack Freight | Logistics / 3PL | ₹4 Cr – ₹5 Cr |
| `transcript_edtech_edupeak.txt` | EduPeak Learning | EdTech | ₹6 Cr – ₹7.5 Cr |
| `transcript_manufacturing_bharatauto.txt` | Bharat Auto Components | Manufacturing / ERP | ₹15 Cr – ₹20 Cr |
| `transcript_media_cinestar.txt` | CineStar OTT | Media / OTT Streaming | ₹10 Cr – ₹13 Cr |

---

## Branch Protection (GitHub Settings)

After pushing to GitHub, protect the `main` branch:
1. Go to **Settings → Branches → Add branch protection rule**
2. Branch name pattern: `main`
3. Enable:
   - ✅ **Require a pull request before merging**
   - ✅ **Require approvals (1)**
   - ✅ **Do not allow bypassing the above settings**
   - ✅ **Restrict who can push to matching branches** (add only yourself)
4. Click **Create**

This ensures no one can push directly to `main` — they can only fork/clone and read the code.

---

## License

Copyright © 2026. All Rights Reserved.

This software is proprietary. You may view and clone this repository for evaluation and educational purposes only. You may **not**:
- Modify or distribute this software
- Use it commercially without explicit written permission
- Claim ownership or re-publish under a different name

See [LICENSE](./LICENSE) for full terms.

---

## Author

Built as an Enterprise Integration AI Agent submission.
Powered by **Groq (Llama 3.3 70B)** · **LangChain** · **FAISS** · **HuggingFace** · **Streamlit**

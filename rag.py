"""
rag.py — Knowledge Base and Retrieval-Augmented Generation module.
Handles document ingestion, vector index management, and semantic retrieval.
"""

import os
import logging
from pathlib import Path
from typing import List, Dict

# Local embeddings so we don't have to pay for OpenAI
from langchain_community.embeddings import HuggingFaceEmbeddings

# Vector store and text splitting tools
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

# ---- Global Paths ----
_APP_DIR = Path(__file__).resolve().parent
_CASE_STUDIES_DIR = _APP_DIR / "case_studies"
_FAISS_INDEX_DIR = _APP_DIR / "faiss_index"


class RAGSystem:
    """
    Retrieval-Augmented Generation system. 
    Manages a FAISS vector database containing internal case studies.
    """

    def __init__(self):
        """
        Initialize the embedding model and vector store.
        Uses sentence-transformers/all-MiniLM-L6-v2 which runs locally on CPU.
        """
        logging.info("Loading embedding model: sentence-transformers/all-MiniLM-L6-v2")
        
        # Load HuggingFace embeddings
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        
        # Will hold the FAISS vector store
        self.index = None
        
        # Load or create
        self.load_or_build_index()

    def load_or_build_index(self):
        """
        Attempt to load an existing FAISS index from disk.
        If it doesn't exist, build a new one from the case_studies folder.
        """
        if _FAISS_INDEX_DIR.exists() and (_FAISS_INDEX_DIR / "index.faiss").exists():
            try:
                logging.info(f"Loading existing FAISS index from {_FAISS_INDEX_DIR}")
                
                self.index = FAISS.load_local(
                    folder_path=str(_FAISS_INDEX_DIR),
                    embeddings=self.embeddings,
                    allow_dangerous_deserialization=True  # Required by FAISS for local files
                )
                
            except Exception as e:
                logging.error(f"Failed to load FAISS index: {e}. Rebuilding...")
                self.rebuild_index()
        else:
            logging.info("No FAISS index found. Building a new one...")
            self.rebuild_index()

    def rebuild_index(self):
        """
        Reads all .txt files from the case_studies directory, chunks them,
        embeds them, builds the FAISS index, and saves it to disk.
        """
        logging.info("Starting FAISS index rebuild...")
        
        if not _CASE_STUDIES_DIR.exists():
            logging.warning(f"Case studies directory missing: {_CASE_STUDIES_DIR}")
            _CASE_STUDIES_DIR.mkdir(parents=True, exist_ok=True)
            
        docs = []
        
        # Read all text files from the case studies folder
        for file_path in _CASE_STUDIES_DIR.glob("*.txt"):
            try:
                loader = TextLoader(str(file_path), encoding="utf-8")
                docs.extend(loader.load())
                logging.info(f"Loaded case study: {file_path.name}")
            except Exception as e:
                logging.error(f"Error loading {file_path.name}: {e}")

        # If empty, create a dummy document so FAISS doesn't crash on build
        if not docs:
            logging.warning("No documents found! Creating empty placeholder index.")
            docs = [Document(page_content="Empty placeholder document", metadata={"source": "none"})]

        # Break case studies into smaller overlapping chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=150,
            separators=["\n\n", "\n", " ", ""]
        )
        
        chunks = text_splitter.split_documents(docs)
        logging.info(f"Split case studies into {len(chunks)} chunks.")
        
        # Create vector index
        self.index = FAISS.from_documents(chunks, self.embeddings)
        
        # Save to disk for future runs
        self.index.save_local(str(_FAISS_INDEX_DIR))
        logging.info("FAISS index successfully rebuilt and saved.")

    def build_retrieval_query(self, insights_dict: dict) -> str:
        """
        Converts the structured JSON output from the TranscriptAnalyzer
        into a semantic query sentence to search the vector database.
        """
        industry = insights_dict.get("industry", "")
        
        # Convert lists to comma-separated strings
        pain_points_list = insights_dict.get("pain_points", [])
        if isinstance(pain_points_list, list):
            pain_points = ", ".join(pain_points_list)
        else:
            pain_points = str(pain_points_list)
            
        desired_outcome_list = insights_dict.get("desired_outcome", [])
        if isinstance(desired_outcome_list, list):
            desired_outcome = ", ".join(desired_outcome_list)
        else:
            desired_outcome = str(desired_outcome_list)
            
        tech_stack_list = insights_dict.get("current_tech_stack", [])
        if isinstance(tech_stack_list, list):
            tech_stack = ", ".join(tech_stack_list)
        else:
            tech_stack = str(tech_stack_list)

        # Construct a natural language query for the similarity search
        query = (
            f"Industry: {industry}. "
            f"Key pain points: {pain_points}. "
            f"Current technology stack: {tech_stack}. "
            f"Desired business outcomes: {desired_outcome}."
        )
        
        return query

    def retrieve_relevant_case_study(self, query: str, top_k: int = 2) -> str:
        """
        Searches the FAISS index for the case study chunks most similar
        to the extracted transcript query.
        Returns the raw text of the matched case study chunks.
        """
        if not self.index:
            return "Knowledge base is currently empty or indexing failed."
            
        logging.info(f"Searching RAG knowledge base for top {top_k} matching case studies...")
        
        # Run similarity search
        docs = self.index.similarity_search(query, k=top_k)
        
        if not docs:
            logging.warning("FAISS search returned no results.")
            return "No relevant case studies found in the internal knowledge base."
            
        # Concatenate the text of the matched chunks
        combined_text = "\n\n---\n\n".join([doc.page_content for doc in docs])
        logging.info("Successfully retrieved relevant case study context.")
        
        return combined_text

"""
agents.py — LLM agents using Groq (FREE — no credit card needed).

Model: llama-3.3-70b-versatile via Groq LPU inference.
Get your FREE Groq API key at: https://console.groq.com
  → Sign Up → API Keys → Create API Key (no card, no billing)
"""

import json
import logging
import re
import sys
from pathlib import Path
from typing import Tuple

from langchain_groq import ChatGroq
from langchain.schema import HumanMessage

_APP_DIR = Path(__file__).resolve().parent
if str(_APP_DIR) not in sys.path:
    sys.path.insert(0, str(_APP_DIR))

from prompts import TRANSCRIPT_ANALYZER_PROMPT, SOLUTION_ARCHITECT_PROMPT

logger = logging.getLogger(__name__)

GROQ_MODEL = "llama-3.3-70b-versatile"


def _build_llm(groq_api_key: str, temperature: float = 0.2) -> ChatGroq:
    """Create a ChatGroq instance (Llama 3.3 70B)."""
    return ChatGroq(
        model=GROQ_MODEL,
        temperature=temperature,
        groq_api_key=groq_api_key,
        max_tokens=4096,
    )


# ---------------------------------------------------------------------------
# Transcript Analyzer Agent
# ---------------------------------------------------------------------------

class TranscriptAnalyzerAgent:
    """
    Uses Groq (Llama 3.3 70B) to extract structured JSON insights
    from a client meeting transcript.
    """

    def __init__(self, groq_api_key: str):
        self.llm = _build_llm(groq_api_key, temperature=0.1)

    def analyze(self, transcript: str) -> Tuple[dict, str]:
        """
        Analyze the transcript and return (parsed_dict, raw_json_string).

        Raises:
            ValueError: If transcript is empty or LLM returns invalid JSON.
            RuntimeError: On API failures.
        """
        if not transcript or not transcript.strip():
            raise ValueError("Transcript is empty. Please upload a non-empty .txt file.")

        if len(transcript.strip()) < 50:
            raise ValueError(
                "Transcript is too short (less than 50 characters). "
                "Please upload a complete meeting transcript."
            )

        prompt_text = TRANSCRIPT_ANALYZER_PROMPT.format(transcript=transcript)

        try:
            logger.info("Calling Transcript Analyzer LLM (Groq / Llama 3.3 70B)...")
            response = self.llm.invoke([HumanMessage(content=prompt_text)])
            raw_output = response.content.strip()
            logger.info("Transcript Analyzer LLM call successful.")
        except Exception as e:
            logger.error(f"LLM API call failed in TranscriptAnalyzerAgent: {e}")
            raise RuntimeError(
                f"Groq API call failed during transcript analysis.\n"
                f"Details: {e}\n"
                "Please check your API key at https://console.groq.com"
            ) from e

        parsed = self._parse_json(raw_output)
        return parsed, raw_output

    def _parse_json(self, raw_output: str) -> dict:
        """Robustly parse JSON with multiple fallback strategies."""
        # 1. Direct parse
        try:
            return json.loads(raw_output)
        except json.JSONDecodeError:
            pass

        # 2. Strip markdown code fences
        json_match = re.search(r"```(?:json)?\s*([\s\S]*?)```", raw_output, re.IGNORECASE)
        if json_match:
            try:
                return json.loads(json_match.group(1).strip())
            except json.JSONDecodeError:
                pass

        # 3. Find first { ... } block
        brace_match = re.search(r"\{[\s\S]*\}", raw_output)
        if brace_match:
            try:
                return json.loads(brace_match.group(0))
            except json.JSONDecodeError:
                pass

        logger.error(f"JSON parsing failed. Raw output:\n{raw_output}")
        raise ValueError(
            "The LLM did not return valid JSON.\n\n"
            f"Raw output received:\n{raw_output[:1000]}"
        )


# ---------------------------------------------------------------------------
# Solution Architect Agent
# ---------------------------------------------------------------------------

class SolutionArchitectAgent:
    """
    Uses Groq (Llama 3.3 70B) to generate a comprehensive Solution
    Design Document from extracted client insights and a retrieved case study.
    """

    def __init__(self, groq_api_key: str):
        self.llm = _build_llm(groq_api_key, temperature=0.4)

    def generate_solution(self, insights: dict, case_study: str) -> str:
        """
        Generate the full Solution Design Document.

        Returns:
            Fully formatted Solution Design Document as Markdown.
        """
        if not insights:
            raise ValueError("Insights dictionary is empty.")
        if not case_study or not case_study.strip():
            case_study = "No relevant case study was retrieved from the knowledge base."

        insights_json = json.dumps(insights, indent=2)
        prompt_text = SOLUTION_ARCHITECT_PROMPT.format(
            insights_json=insights_json,
            case_study=case_study,
        )

        try:
            logger.info("Calling Solution Architect LLM (Groq / Llama 3.3 70B)...")
            response = self.llm.invoke([HumanMessage(content=prompt_text)])
            document = response.content.strip()
            logger.info("Solution Architect LLM call successful.")
        except Exception as e:
            logger.error(f"LLM API call failed in SolutionArchitectAgent: {e}")
            raise RuntimeError(
                f"Groq API call failed during solution generation.\n"
                f"Details: {e}"
            ) from e

        if not document:
            raise RuntimeError("LLM returned an empty response.")

        return document

"""
prompts.py — All LangChain PromptTemplates for the Sales Engineer AI Agent.
"""

from langchain.prompts import PromptTemplate


# ---------------------------------------------------------------------------
# Transcript Analyzer Prompt
# ---------------------------------------------------------------------------

TRANSCRIPT_ANALYZER_TEMPLATE = """
You are a senior enterprise sales engineer and business analyst.
Carefully read the following client meeting transcript and extract structured information.

TRANSCRIPT:
-----------
{transcript}
-----------

Extract the following and return ONLY a valid JSON object with these exact keys:
{{
  "client_name": "<Name of the client company, or 'Unknown' if not mentioned>",
  "industry": "<Industry vertical, e.g. Fintech, Healthcare, E-Commerce, etc.>",
  "pain_points": [
    "<Pain point 1>",
    "<Pain point 2>",
    "<Pain point 3 — add more as needed>"
  ],
  "current_tech_stack": [
    "<Technology / system 1>",
    "<Technology / system 2>",
    "<Add more as found in the transcript>"
  ],
  "desired_outcome": [
    "<Desired outcome 1>",
    "<Desired outcome 2>",
    "<Add more as needed>"
  ],
  "budget_range": "<Mentioned budget range expressed in Indian Rupees (₹). Convert if stated in USD: 1 USD ≈ ₹83. Use Crore/Lakh notation where appropriate (e.g. ₹5 Crore - ₹6.5 Crore), or 'Not specified' if absent>",
  "timeline": "<Mentioned project timeline, or 'Not specified'>",
  "decision_maker": "<Name/role of decision-maker if mentioned, or 'Not specified'>"
}}

STRICT RULES:
- Return ONLY the JSON object. No preamble, no explanation, no markdown fences.
- All list values must be non-empty strings.
- If information is truly absent from the transcript, use "Not specified" for strings or ["Not mentioned"] for lists.
- Do NOT invent information. Only use what is in the transcript.
- This is an Indian enterprise market platform — express all monetary values in Indian Rupees (₹).
"""

TRANSCRIPT_ANALYZER_PROMPT = PromptTemplate(
    input_variables=["transcript"],
    template=TRANSCRIPT_ANALYZER_TEMPLATE,
)


# ---------------------------------------------------------------------------
# Solution Architect Prompt
# ---------------------------------------------------------------------------

SOLUTION_ARCHITECT_TEMPLATE = """
You are a world-class enterprise solution architect and sales engineer.
Your task is to produce a comprehensive, professional Solution Design Document
for a potential client, based on the extracted insights from their meeting transcript
and a relevant internal case study retrieved from our knowledge base.

---
EXTRACTED CLIENT INSIGHTS (JSON):
{insights_json}

---
RELEVANT CASE STUDY FROM OUR KNOWLEDGE BASE:
{case_study}

---

Generate a detailed Solution Design Document using the exact structure below.
Use professional language suitable for executive and technical stakeholders.
Be specific — reference technologies, patterns, and the case study where relevant.

---

# Solution Design Document

## 1. Client Overview
Provide a brief executive summary of the client, their industry, and the context of this engagement.

## 2. Identified Pain Points
List and briefly explain each pain point identified from the transcript.
For each, note the business impact if left unresolved.

## 3. Current Tech Stack Assessment
Analyze the client's existing technology landscape.
Identify gaps, risks, and legacy constraints.

## 4. Desired Outcomes
Clearly state what success looks like for the client.
Map each outcome to a measurable metric where possible.

## 5. Recommended Architecture
Describe the proposed solution architecture in detail.
Include:
- Architecture pattern (microservices, event-driven, serverless, etc.)
- Key components and their roles
- Data flow overview
- Scalability and resilience considerations

## 6. Integration Strategy
Explain how the new architecture integrates with existing systems.
Cover:
- Integration patterns (API Gateway, Event Bus, ETL, etc.)
- Data migration approach
- Backward compatibility handling

## 7. Technology Suggestions
Provide a curated list of recommended technologies with justification for each:
- Backend / API layer
- Frontend / UI (if applicable)
- Database / Data layer
- Cloud / Infrastructure
- Monitoring & Observability
- Security

## 8. Implementation Roadmap
Break the project into phases with estimated timelines:
- Phase 1: Foundation & Quick Wins
- Phase 2: Core Integration
- Phase 3: Advanced Features & Optimization
- Phase 4: Go-Live & Stabilization

## 9. Relevant Case Study Reference
Summarize the most relevant case study from our portfolio.
Draw explicit parallels between that client's challenges and this client's situation.
Highlight the results achieved to build confidence.

## 10. Risks & Mitigations
Identify the top 3–5 project risks and recommended mitigation strategies.

## 11. Next Steps
List 3–5 concrete, actionable next steps to move this engagement forward
(e.g., technical discovery session, PoC scope definition, stakeholder alignment call).

---
Generate the full document now. Be thorough, professional, and persuasive.
"""

SOLUTION_ARCHITECT_PROMPT = PromptTemplate(
    input_variables=["insights_json", "case_study"],
    template=SOLUTION_ARCHITECT_TEMPLATE,
)

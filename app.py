"""
app.py — Production UI for the Enterprise Integration Sales Engineer AI Agent
"""

import sys
import os
import json
import logging
from pathlib import Path

_APP_DIR = Path(__file__).resolve().parent
if str(_APP_DIR) not in sys.path:
    sys.path.insert(0, str(_APP_DIR))

import streamlit as st
from agents import TranscriptAnalyzerAgent, SolutionArchitectAgent
from rag import RAGSystem

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def get_api_key() -> str:
    try:
        key = st.secrets.get("GROQ_API_KEY", "")
        if key:
            return key
    except Exception:
        pass
    return os.environ.get("GROQ_API_KEY", "")


# ─── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Enterprise Solution Architect AI",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── CSS ──────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
    background-color: #060b14 !important;
    color: #e2e8f0 !important;
}

/* Sidebar */
[data-testid="stSidebar"] { background: #0a1120 !important; border-right: 1px solid #1a2744; }

/* Hero */
.hero-wrap {
    background: linear-gradient(135deg, #0e1f40 0%, #091830 50%, #0c2250 100%);
    border: 1px solid #1e3a7a;
    border-radius: 22px;
    padding: 3.5rem 3rem 3rem;
    margin-bottom: 2.5rem;
    position: relative;
    overflow: hidden;
    text-align: center;
}
.hero-wrap::before {
    content: '';
    position: absolute; top: -80px; right: -80px;
    width: 320px; height: 320px;
    background: radial-gradient(circle, rgba(56,189,248,0.09) 0%, transparent 65%);
    border-radius: 50%;
}
.hero-wrap::after {
    content: '';
    position: absolute; bottom: -60px; left: -60px;
    width: 240px; height: 240px;
    background: radial-gradient(circle, rgba(99,102,241,0.08) 0%, transparent 65%);
    border-radius: 50%;
}
.hero-badge {
    display: inline-flex; align-items: center; gap: 8px;
    background: rgba(56,189,248,0.1);
    border: 1px solid rgba(56,189,248,0.25);
    color: #38bdf8;
    border-radius: 50px;
    padding: 5px 16px;
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 1.8px;
    text-transform: uppercase;
    margin-bottom: 1.2rem;
}
.hero-wrap h1 {
    font-size: 2.8rem;
    font-weight: 900;
    color: #f8fafc;
    line-height: 1.12;
    letter-spacing: -1.5px;
    margin-bottom: 1rem;
}
.hero-wrap h1 em { font-style: normal; color: #38bdf8; }
.hero-sub {
    color: #94a3b8;
    font-size: 1.1rem;
    line-height: 1.65;
    max-width: 680px;
    margin: 0 auto;
    text-align: center;
}
.hero-stats {
    display: flex; gap: 2rem;
    justify-content: center;
    margin-top: 2rem;
    padding-top: 2rem;
    border-top: 1px solid rgba(30,58,122,0.6);
}
.hero-stat-val { font-size: 1.6rem; font-weight: 800; color: #38bdf8; }
.hero-stat-lbl { font-size: 0.72rem; color: #64748b; text-transform: uppercase; letter-spacing: 0.8px; margin-top: 2px; }

/* Cards */
.card {
    background: rgba(13,25,52,0.7);
    border: 1px solid #1e3a7a;
    border-radius: 14px;
    padding: 1.5rem;
    margin-bottom: 1rem;
    backdrop-filter: blur(4px);
}
.card-title {
    font-size: 0.72rem;
    font-weight: 700;
    color: #475569;
    text-transform: uppercase;
    letter-spacing: 1.2px;
    margin-bottom: 0.6rem;
}

/* Upload area */
.upload-card {
    background: rgba(13,25,52,0.5);
    border: 2px dashed #1e3a7a;
    border-radius: 14px;
    padding: 0.8rem;
    transition: border-color 0.2s;
    margin-bottom: 0.8rem;
}
.upload-card:hover { border-color: #38bdf8; }

/* File info chips */
.chip {
    display: inline-flex; align-items: center; gap: 5px;
    background: rgba(30,58,122,0.4);
    border: 1px solid rgba(30,58,122,0.8);
    color: #7dd3fc;
    border-radius: 6px;
    padding: 3px 10px;
    font-size: 0.78rem;
    font-weight: 500;
    margin: 2px;
}
.chip-success {
    background: rgba(4,120,87,0.2);
    border-color: rgba(6,95,70,0.8);
    color: #6ee7b7;
}
.chip-danger {
    background: rgba(127,29,29,0.25);
    border-color: rgba(153,27,27,0.8);
    color: #fca5a5;
}

/* Generate button */
div.stButton > button {
    background: linear-gradient(90deg, #0369a1, #0ea5e9) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.85rem 2.5rem !important;
    font-weight: 800 !important;
    font-size: 1rem !important;
    letter-spacing: 0.2px !important;
    width: 100% !important;
    box-shadow: 0 4px 20px rgba(14,165,233,0.35) !important;
    transition: all 0.2s !important;
}
div.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 28px rgba(14,165,233,0.5) !important;
}

/* Progress */
.stProgress > div > div { background: linear-gradient(90deg, #0369a1, #38bdf8) !important; border-radius: 10px !important; }
.stProgress { background: rgba(30,58,122,0.3) !important; border-radius: 10px !important; }

/* Pain point item */
.pain-item {
    display: flex; align-items: flex-start; gap: 12px;
    background: rgba(127,29,29,0.15);
    border: 1px solid rgba(153,27,27,0.4);
    border-radius: 10px;
    padding: 0.9rem 1.1rem;
    margin-bottom: 0.6rem;
}
.pain-num {
    background: rgba(239,68,68,0.2); border: 1px solid rgba(239,68,68,0.4);
    color: #f87171; border-radius: 50%;
    min-width: 26px; height: 26px;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.75rem; font-weight: 700; flex-shrink: 0;
}
.pain-text { color: #fca5a5; font-size: 0.88rem; line-height: 1.5; padding-top: 1px; }

/* Outcome item */
.outcome-item {
    display: flex; align-items: flex-start; gap: 10px;
    padding: 0.6rem 0;
    border-bottom: 1px solid rgba(30,58,122,0.3);
    color: #cbd5e1;
    font-size: 0.88rem;
}
.outcome-item:last-child { border-bottom: none; }

/* Two-column insight grid */
.insight-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 1rem; }
.insight-box {
    background: rgba(13,25,52,0.6);
    border: 1px solid #1e3a7a;
    border-radius: 10px;
    padding: 1rem 1.2rem;
}
.insight-lbl { font-size: 0.7rem; font-weight: 700; color: #475569; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 0.4rem; }
.insight-val { font-size: 0.92rem; font-weight: 600; color: #e2e8f0; }

/* Banner */
.banner {
    display: flex; align-items: center; gap: 12px;
    background: linear-gradient(90deg, rgba(5,46,22,0.6), rgba(20,83,45,0.3));
    border: 1px solid #166534;
    border-radius: 12px;
    padding: 1rem 1.4rem;
    color: #86efac;
    font-weight: 700;
    font-size: 1rem;
    margin: 1.5rem 0 1rem;
}
.banner-icon { font-size: 1.5rem; }

/* Solution doc */
.doc-body {
    background: rgba(10,18,38,0.8);
    border: 1px solid #1e3a7a;
    border-radius: 14px;
    padding: 2.5rem 3rem;
    line-height: 1.75;
}
.doc-body h1, .doc-body h2 { color: #38bdf8 !important; }
.doc-body h3 { color: #7dd3fc !important; }
.doc-body h1 { border-bottom: 1px solid #1e3a7a; padding-bottom: 0.5rem; margin-bottom: 1rem; }
.doc-body h2 { margin-top: 2rem; margin-bottom: 0.8rem; }
.doc-body li { color: #cbd5e1; }
.doc-body strong { color: #e2e8f0; }

/* Download buttons */
.stDownloadButton > button {
    background: rgba(13,25,52,0.8) !important;
    border: 1px solid #1e3a7a !important;
    color: #7dd3fc !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
}
.stDownloadButton > button:hover {
    border-color: #38bdf8 !important;
    background: rgba(14,165,233,0.1) !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: rgba(10,18,38,0.9);
    border-radius: 12px;
    border: 1px solid #1e3a7a;
    padding: 5px; gap: 4px;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px !important;
    color: #64748b !important;
    font-weight: 600 !important;
    font-size: 0.88rem !important;
    background: transparent !important;
    padding: 8px 20px !important;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #0369a1, #0284c7) !important;
    color: white !important;
}

/* Spinner */
.stSpinner > div { border-top-color: #38bdf8 !important; }

/* Hide streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ─── API Key ──────────────────────────────────────────────────────────────────
api_key = get_api_key()

# ─── Hero ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-wrap">
    <div class="hero-badge">⚡ TALK · ANALYZE · ARCHITECT</div>
    <h1>The Enterprise Integration<br><em>Sales Engineer</em></h1>
    <p class="hero-sub" style="text-align:center;margin:0 auto;">
        Transform raw client discovery call recordings into professional, board-ready
        <strong style="color:#e2e8f0;">Solution Design Documents</strong> automatically.
        Powered by enterprise knowledge retrieval.
    </p>
    <div class="hero-stats">
        <div>
            <div class="hero-stat-val">60s</div>
            <div class="hero-stat-lbl">Avg generation time</div>
        </div>
        <div>
            <div class="hero-stat-val">Easy to use</div>
            <div class="hero-stat-lbl">Upload and get the solution</div>
        </div>
        <div>
            <div class="hero-stat-val">From Talk to Tech</div>
            <div class="hero-stat-lbl">Intelligence</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ─── Main Layout ──────────────────────────────────────────────────────────────
upload_col, result_col = st.columns([1, 1.4], gap="large")

with upload_col:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">📁 Upload Client Transcript</div>', unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "Upload transcript",
        type=["txt"],
        label_visibility="collapsed",
    )

    if uploaded_file:
        transcript_text = uploaded_file.read().decode("utf-8", errors="replace")
        word_count = len(transcript_text.split())
        st.markdown(f"""
        <div style="margin: 10px 0 14px;">
            <span class="chip">📄 {uploaded_file.name}</span>
            <span class="chip">📝 {word_count} words</span>
        </div>
        """, unsafe_allow_html=True)
        with st.expander("Preview transcript"):
            st.text_area(
                "Transcript content",
                value=transcript_text[:2000] + ("…" if len(transcript_text) > 2000 else ""),
                height=160,
                label_visibility="collapsed",
                disabled=True,
            )
    else:
        st.markdown("""
        <div style="text-align:center;padding:2rem 0;color:#475569;">
            <div style="font-size:2.5rem;margin-bottom:0.5rem;">📄</div>
            <div style="font-size:0.88rem;">Drop your meeting transcript (.txt) here</div>
            <div style="font-size:0.78rem;margin-top:0.4rem;color:#334155;">Any format — conversation, notes, or recording transcript</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="card" style="border-color:#0f3460;">', unsafe_allow_html=True)
    st.markdown('<div class="card-title" style="text-align:center;">ℹ️ How It Works</div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="font-size:0.85rem;line-height:2.4;color:#94a3b8;text-align:center;">
        <div>① Upload any client meeting transcript (.txt)</div>
        <div>② AI extracts client needs &amp; pain points</div>
        <div>③ Knowledge base matches relevant case studies</div>
        <div>④ Solution Design Document is generated</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    if not api_key:
        st.error("⚠️ API key not configured. Contact the platform administrator.")
    else:
        generate_btn = st.button("🚀  Generate Solution Design Document", use_container_width=True)

with result_col:
    if not uploaded_file:
        st.markdown("""
        <div style="
            background: rgba(13,25,52,0.4);
            border: 1px dashed #1a2744;
            border-radius: 16px;
            height: 480px;
            display: flex; flex-direction: column;
            align-items: center; justify-content: center;
            color: #334155; text-align: center; padding: 2rem;
        ">
            <div style="font-size:3.5rem;margin-bottom:1rem;filter:grayscale(1);opacity:0.5;">📋</div>
            <div style="font-size:1.1rem;font-weight:600;color:#475569;">Your Solution Document Will Appear Here</div>
            <div style="font-size:0.85rem;margin-top:0.5rem;color:#334155;">Upload a transcript and click Generate to begin</div>
        </div>
        """, unsafe_allow_html=True)

# ─── Generation Pipeline ──────────────────────────────────────────────────────
if api_key and uploaded_file:
    if generate_btn:
        uploaded_file.seek(0)
        transcript_text = uploaded_file.read().decode("utf-8", errors="replace")

        progress = st.progress(0, text="🚀 Starting AI pipeline…")

        try:
            # Step 1
            progress.progress(10, text="🔍 Analyzing client transcript…")
            with st.spinner("Understanding client needs…"):
                analyzer = TranscriptAnalyzerAgent(groq_api_key=api_key)
                insights_dict, _ = analyzer.analyze(transcript_text)
            progress.progress(33, text="✅ Client analysis complete")

            # Step 2
            progress.progress(40, text="🔎 Searching knowledge base for relevant case studies…")
            with st.spinner("Retrieving most relevant case study…"):
                rag = RAGSystem()
                retrieval_query = rag.build_retrieval_query(insights_dict)
                retrieved_case_study = rag.retrieve_relevant_case_study(retrieval_query, top_k=1)
            progress.progress(66, text="✅ Case study matched")

            # Step 3
            progress.progress(70, text="🏗️ Generating Solution Design Document…")
            with st.spinner("Crafting your solution document…"):
                architect = SolutionArchitectAgent(groq_api_key=api_key)
                solution_document = architect.generate_solution(insights_dict, retrieved_case_study)
            progress.progress(100, text="✅ Complete!")

            # ── Results ──────────────────────────────────────────────────────
            client      = insights_dict.get("client_name", "Client")
            industry    = insights_dict.get("industry", "")
            budget      = insights_dict.get("budget_range", "Not specified")
            timeline    = insights_dict.get("timeline", "Not specified")
            decision_mk = insights_dict.get("decision_maker", "Not specified")
            pain_points = insights_dict.get("pain_points", [])
            tech_stack  = insights_dict.get("current_tech_stack", [])
            outcomes    = insights_dict.get("desired_outcome", [])

            st.markdown(f"""
            <div class="banner">
                <span class="banner-icon">🎉</span>
                Solution Design Document ready for <strong style="color:#4ade80;">&nbsp;{client}</strong>
            </div>
            """, unsafe_allow_html=True)

            # Client summary strip
            st.markdown(f"""
            <div style="display:flex;flex-wrap:wrap;gap:6px;margin-bottom:1.5rem;">
                <span class="chip">🏢 {client}</span>
                <span class="chip">🏭 {industry}</span>
                <span class="chip">💰 {budget}</span>
                <span class="chip">📅 {timeline}</span>
            </div>
            """, unsafe_allow_html=True)

            tab_analysis, tab_doc = st.tabs(["📊  Client Analysis", "📄  Solution Document"])

            # ── Tab 1: Client Analysis ────────────────────────────────────────
            with tab_analysis:
                # Key info grid
                st.markdown(f"""
                <div class="insight-grid">
                    <div class="insight-box">
                        <div class="insight-lbl">👤 Decision Maker</div>
                        <div class="insight-val">{decision_mk}</div>
                    </div>
                    <div class="insight-box">
                        <div class="insight-lbl">🏭 Industry</div>
                        <div class="insight-val">{industry}</div>
                    </div>
                    <div class="insight-box">
                        <div class="insight-lbl">💰 Budget Range</div>
                        <div class="insight-val">{budget}</div>
                    </div>
                    <div class="insight-box">
                        <div class="insight-lbl">📅 Timeline</div>
                        <div class="insight-val">{timeline}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # Pain points
                if pain_points:
                    st.markdown('<div style="font-size:0.8rem;font-weight:700;color:#f87171;letter-spacing:1px;text-transform:uppercase;margin:1rem 0 0.6rem;">⚠️ Identified Pain Points</div>', unsafe_allow_html=True)
                    for i, pp in enumerate(pain_points):
                        st.markdown(f"""
                        <div class="pain-item">
                            <div class="pain-num">{i+1}</div>
                            <div class="pain-text">{pp}</div>
                        </div>
                        """, unsafe_allow_html=True)

                col1, col2 = st.columns(2)
                with col1:
                    if tech_stack:
                        st.markdown('<div style="font-size:0.8rem;font-weight:700;color:#7dd3fc;letter-spacing:1px;text-transform:uppercase;margin:1rem 0 0.6rem;">🛠️ Current Tech Stack</div>', unsafe_allow_html=True)
                        for t in tech_stack:
                            st.markdown(f'<span class="chip">⚙️ {t}</span>', unsafe_allow_html=True)

                with col2:
                    if outcomes:
                        st.markdown('<div style="font-size:0.8rem;font-weight:700;color:#6ee7b7;letter-spacing:1px;text-transform:uppercase;margin:1rem 0 0.6rem;">🎯 Desired Outcomes</div>', unsafe_allow_html=True)
                        for o in outcomes:
                            st.markdown(f"""
                            <div class="outcome-item">
                                <span style="color:#4ade80;flex-shrink:0;">✓</span> {o}
                            </div>
                            """, unsafe_allow_html=True)

            # ── Tab 2: Solution Document ──────────────────────────────────────
            with tab_doc:
                st.markdown(f"""
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:1rem;">
                    <div style="font-size:0.8rem;color:#64748b;">{len(solution_document.split())} words · {len(solution_document.splitlines())} lines</div>
                </div>
                """, unsafe_allow_html=True)

                with st.container():
                    st.markdown(solution_document)

                st.markdown("---")
                safe_name = client.replace(" ", "_").lower()
                dl1, dl2, _ = st.columns([1, 1, 2])
                with dl1:
                    st.download_button(
                        "⬇️ Download .md",
                        data=solution_document,
                        file_name=f"solution_{safe_name}.md",
                        mime="text/markdown",
                        use_container_width=True,
                    )
                with dl2:
                    st.download_button(
                        "⬇️ Download .txt",
                        data=solution_document,
                        file_name=f"solution_{safe_name}.txt",
                        mime="text/plain",
                        use_container_width=True,
                    )

        except ValueError as ve:
            st.error(f"⚠️ {ve}")
        except RuntimeError as rte:
            st.error(f"❌ {rte}")
        except Exception as ex:
            st.error(f"❌ Unexpected error: {ex}")
            logger.exception("Unexpected error in pipeline.")

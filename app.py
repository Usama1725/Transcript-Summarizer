import streamlit as st
from typing import List
from langchain_community.chat_models import ChatOllama
from langchain.prompts import ChatPromptTemplate
from langchain.text_splitter import RecursiveCharacterTextSplitter

import re
import io
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

st.set_page_config(page_title="Transcript → Bullets (Local)", page_icon="▶️", layout="wide")
st.title("📄 Paste Transcript → 🔹 Bullet Summary (Local/Ollama)")


def normalize_bullets(text: str) -> list[str]:
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    if len(lines) <= 1:
        parts = re.split(r"[•\-\*\u2022]\s+", lines[0]) if lines else []
        lines = [p.strip() for p in parts if p.strip()] or lines

    bullets = []
    for s in lines:
        s = re.sub(r"^\s*(?:[-–—*•·o◦○]+|\d+[\.\)]\s*)\s*", "", s)  # strip leading markers
        s = re.sub(r"\s+", " ", s).strip()
        if s and s not in bullets:
            bullets.append(s)
    return bullets



def to_bullets(text: str):
    # grab lines that already start with a bullet, or split on "•"
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    bullets = []
    for s in lines:
        if s.startswith(("-", "•")):
            bullets.append(s.lstrip("-• ").strip())
    if not bullets:
        bullets = [s.strip() for s in text.split("•") if s.strip()]
    # de-dup and keep short
    seen = set()
    out = []
    for b in bullets:
        if b not in seen:
            seen.add(b)
            out.append(b)
    return out

def build_bullets_pdf(title: str, bullets: list[str]) -> bytes:
    # Clean any leading markers just in case
    cleaned = []
    for b in bullets:
        s = re.sub(r"^\s*(?:[-–—*•·o◦○]+|\d+[\.\)]\s*)\s*", "", b or "").strip()
        if s:
            cleaned.append(s)

    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=letter,
        leftMargin=54, rightMargin=54, topMargin=54, bottomMargin=54
    )
    styles = getSampleStyleSheet()
    title_style = styles["Title"]

    bullet_style = ParagraphStyle(
        name="Bullet",
        parent=styles["BodyText"],
        leftIndent=18,       # indent of the bullet body
        bulletIndent=0,      # where the bullet sits
        spaceBefore=2,
        spaceAfter=2,
        leading=14,
    )

    story = [Paragraph(title, title_style), Spacer(1, 12)]
    for s in cleaned:
        story.append(Paragraph(s, bullet_style, bulletText="•"))

    doc.build(story)
    buf.seek(0)
    return buf.getvalue()

# ---------- Sidebar (minimal settings) ----------
with st.sidebar:
    model = st.selectbox(
        "Local model (must be pulled via Ollama)",
        ["llama3.2:3b", "llama3.1:8b", "mistral:7b"],
        index=0,
    )
    temperature = st.slider("Creativity (temperature)", 0.0, 1.0, 0.1, 0.1)
    chunk_size = st.number_input("Chunk size (chars)", min_value=500, max_value=3000, value=1500, step=100)
    overlap = st.number_input("Chunk overlap (chars)", min_value=0, max_value=500, value=150, step=50)
    k_context = st.slider("Max chunks to use", 1, 12, 6)
    st.caption("Tip: Start with llama3.2:3b for speed, then try 7–8B models for quality.")

# ---------- Input ----------
raw_text = st.text_area(
    "Paste transcript text below",
    height=300,
    placeholder="Paste the video's transcript text here…",
)

# ---------- Prompt ----------
SYSTEM = (
    "You are a precise, helpful assistant. Use only the provided transcript text. "
    "If something isn't present, say you don't know. Return concise bullet points."
)
BULLETS_PROMPT = ChatPromptTemplate.from_messages([
    ("system", "You are a precise assistant. Use only the transcript. Return ONLY markdown bullets, one per line, no intro/outro."),
    ("human",
     "Summarize the transcript into 6–12 concise bullets (≤ ~20 words each).\n\n"
     "Transcript:\n{context}\n")
])


# ---------- Helpers ----------
def chunk_text(text: str) -> List[str]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=int(chunk_size),
        chunk_overlap=int(overlap),
        separators=["\n\n", "\n", " ", ""]
    )
    docs = splitter.create_documents([text])
    return [d.page_content for d in docs]


# ---------- Generate Bullets ----------
if st.button("Generate bullets"):
    if not raw_text.strip():
        st.warning("Please paste some transcript text first.")
    else:
        # build context
        chunks = chunk_text(raw_text.strip())
        selected = chunks[:k_context]
        context = "\n\n---\n\n".join(selected)

        # run local model
        llm = ChatOllama(model="llama3.2:3b", temperature=temperature, base_url="http://127.0.0.1:11434")
        with st.spinner("Summarizing locally…"):
            msg = BULLETS_PROMPT.format_messages(context=context)
            resp = llm.invoke(msg)

        # >>> YOUR SNIPPET GOES HERE <<<
        bullets = normalize_bullets(resp.content)

        st.subheader("Bullets Output")
        if bullets:
            # show as Markdown
            st.markdown("\n".join(f"- {b}" for b in bullets))

            # build & download PDF
            pdf_bytes = build_bullets_pdf("Bullet Summary", bullets)
            st.download_button(
                "Download PDF",
                data=pdf_bytes,
                file_name="summary.pdf",
                mime="application/pdf",
            )
        else:
            st.markdown(resp.content)  # fallback if parsing fails

        with st.expander("Transcript preview"):
            st.code(raw_text[:1000] + ("…" if len(raw_text) > 1000 else ""))
        st.caption(f"Used {len(selected)} chunk(s) out of {len(chunks)}.")

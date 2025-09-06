"""
Streamlit Prompt Enhancer
-------------------------
Builds a better prompt from Role, Context, and Task.
Outputs the improved prompt only (in three formats).

• Uses the latest OpenAI Python SDK and the Responses API.
• Asks for the user's OpenAI API key securely on-screen (not stored).
• Ensures the enhanced prompt ALWAYS instructs GPT to clarify assumptions before responding.
• Does NOT echo the Role, Context, or Task back in outputs — only produces the enhanced prompt text.

Author: You
"""
from __future__ import annotations

import html
import json
import streamlit as st
from openai import OpenAI

# ---------------------------
# Streamlit Page Config
# ---------------------------
st.set_page_config(
    page_title="✨ Prompt Enhancer",
    page_icon="✨",
    layout="centered",
)

st.title("✨ Prompt Enhancer")
st.caption("Turn Role • Context • Task into a more elaborate, professional prompt")

# ---------------------------
# Sidebar — API & Model Controls
# ---------------------------
with st.sidebar:
    st.subheader("API Settings")
    api_key = st.text_input(
        "OpenAI API Key",
        type="password",
        placeholder="sk-...",
        help=(
            "Your key is only used in this session to call OpenAI. "
            "It is not saved to disk or sent anywhere else."
        ),
    )

    model = st.selectbox(
        "Model",
        options=["gpt-4o-mini", "gpt-4o"],
        index=0,
        help="Choose a text-capable model.",
    )

    temperature = st.slider(
        "Creativity (temperature)", 0.0, 1.2, 0.5, 0.1,
        help="Lower = more focused. Higher = more creative.",
    )

    max_output_chars = st.number_input(
        "Max characters for improved prompt",
        min_value=400,
        max_value=10000,
        value=2000,
        step=50,
    )

# ---------------------------
# Inputs — Role, Context, Task
# ---------------------------
st.subheader("Your Inputs")
role = st.text_input("Role", placeholder="e.g., You are an experienced Python developer.")
context = st.text_area("Context", height=120, placeholder="e.g., I am a beginner learning to code.")
task = st.text_area("Task", height=140, placeholder="e.g., Help me build an app that enhances prompts.")

st.info("This app only generates an improved prompt. It does **not** execute the prompt.")

# ---------------------------
# Helpers
# ---------------------------
ASSUMPTIONS_LINE = (
    "Before responding, explicitly list any assumptions, identify missing information, and ask clarifying questions as needed."
)

SYSTEM_INSTRUCTIONS = (
    "You are a senior prompt engineer. Rewrite the user’s Role, Context, and Task into a much more elaborate, polished, and professional instruction prompt. "
    "The result must be self-contained, expand upon the role, context, and task in a structured way, provide extra clarity and detail, and be more robust than the original instructions. "
    "Explicitly include this clause: '" + ASSUMPTIONS_LINE + "'. Do not answer the task — only output the improved prompt itself."
)


def ensure_assumptions_clause(text: str) -> str:
    if not text:
        return text
    if "assumption" not in text.lower():
        text = text.rstrip() + "\n\nAssumptions & Clarifications:\n- " + ASSUMPTIONS_LINE
    return text


def to_xml(improved_prompt: str) -> str:
    return f"<enhancedPrompt>\n{html.escape(improved_prompt)}\n</enhancedPrompt>"


def to_json(improved_prompt: str):
    return {"enhanced_prompt": improved_prompt}

# ---------------------------
# Action — Generate Improved Prompt
# ---------------------------
if st.button("Generate Improved Prompt ✨", type="primary"):
    if not api_key:
        st.error("Please paste your OpenAI API key in the sidebar.")
        st.stop()
    if not (role or context or task):
        st.error("Please provide Role, Context, or Task.")
        st.stop()

    base_prompt = f"Role: {role}\nContext: {context}\nTask: {task}"

    client = OpenAI(api_key=api_key)

    with st.spinner("Calling OpenAI to enhance your prompt..."):
        try:
            resp = client.responses.create(
                model=model,
                temperature=float(temperature),
                instructions=SYSTEM_INSTRUCTIONS,
                input=[{"role": "user", "content": [{"type": "input_text", "text": base_prompt}]}],
            )
            improved = getattr(resp, "output_text", None) or ""
        except Exception as e:
            st.error(f"OpenAI API error: {e}")
            st.stop()

    improved = ensure_assumptions_clause(improved)
    if len(improved) > max_output_chars:
        improved = improved[: max_output_chars - 3].rstrip() + "..."

    xml_text = to_xml(improved)
    json_obj = to_json(improved)

    st.success("Enhanced prompt generated!")

    tabs = st.tabs(["Plain text", "XML", "JSON"])
    with tabs[0]:
        st.code(improved, language="markdown")
    with tabs[1]:
        st.code(xml_text, language="xml")
    with tabs[2]:
        st.code(json.dumps(json_obj, indent=2, ensure_ascii=False), language="json")

st.divider()
st.caption("The output above is the enhanced prompt only — clearer, more elaborate, and professional.")

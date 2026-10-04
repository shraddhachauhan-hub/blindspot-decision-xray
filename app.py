import json
import os
import re

import streamlit as st
from google import genai


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="BlindSpot — Decision X-Ray",
    page_icon="🧠",
    layout="wide",
)


# ============================================================
# STYLING
# ============================================================

st.markdown(
    """
    <style>
        .main {
            padding-top: 1rem;
        }

        .hero {
            padding: 1.5rem 0 1rem 0;
        }

        .hero h1 {
            font-size: 3rem;
            margin-bottom: 0.2rem;
        }

        .subtitle {
            font-size: 1.15rem;
            opacity: 0.75;
        }

        .tag {
            display: inline-block;
            padding: 0.35rem 0.7rem;
            margin: 0.2rem;
            border: 1px solid rgba(128,128,128,0.35);
            border-radius: 999px;
            font-size: 0.85rem;
        }

        .card {
            padding: 1.2rem;
            border: 1px solid rgba(128,128,128,0.25);
            border-radius: 14px;
            margin-bottom: 1rem;
            background: rgba(128,128,128,0.04);
        }

        .small {
            font-size: 0.85rem;
            opacity: 0.7;
        }

        .section-space {
            margin-top: 1rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# HEADER
# ============================================================

st.markdown(
    """
    <div class="hero">
        <div class="small">AI Decision Reflection • PromptWars</div>
        <h1>🧠 BlindSpot</h1>
        <div class="subtitle">
            <b>Decision X-Ray</b> — don't ask AI what to choose.
            Ask it what you might be missing.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <span class="tag">Hidden assumptions</span>
    <span class="tag">Bias signals</span>
    <span class="tag">Trade-offs</span>
    <span class="tag">Multiple perspectives</span>
    <span class="tag">Questions, not verdicts</span>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# SYSTEM PROMPT
# ============================================================

SYSTEM_PROMPT = """
You are BlindSpot, an AI decision-reflection assistant.

Your purpose is NOT to make decisions for the user.

Your job is to examine the user's reasoning and identify:
1. What they are explicitly focusing on.
2. What they may be overlooking.
3. Hidden assumptions.
4. Possible cognitive bias signals.
5. Trade-offs and tensions.
6. Different perspectives.
7. Questions they should explore.
8. Evidence they should verify.
9. Conditions that could genuinely change their thinking.

IMPORTANT RULES:

- Never make the decision for the user.
- Never give a verdict.
- Never tell the user to accept, reject, buy, sell, quit, invest, choose, or avoid an option.
- Never provide numerical probabilities.
- Prefer questions over advice.
- Be specific to the user's situation.
- Do not invent facts.
- Do not invent statistics, probabilities, research findings, or external claims.
- Do not make broad claims about industries, startups, markets, people, or outcomes unless the user provided evidence for them.
- If an external claim would require evidence, frame it as a question or uncertainty instead.
- Separate observations from uncertainty.
- Do not pretend to know the user's emotions.
- If information is missing, say so.
- Keep insights practical and specific rather than generic.

For bias signals, identify only plausible signals based on the user's reasoning.
Do not diagnose the user.

For blind spots, explain why each missing factor matters.

For evidence, identify concrete information that could be verified.

For "what could change your mind", identify conditions or evidence that could challenge the user's current thinking.

Return ONLY valid JSON.

Use exactly this structure:

{
  "decision_snapshot": "",
  "visible_focus": [
    "",
    "",
    ""
  ],
  "blind_spots": [
    {
      "title": "",
      "description": "",
      "why_it_matters": ""
    }
  ],
  "hidden_assumptions": [
    {
      "assumption": "",
      "status": "",
      "question": ""
    }
  ],
  "bias_signals": [
    {
      "bias": "",
      "signal": "",
      "counter_question": ""
    }
  ],
  "tradeoffs": [
    {
      "gain": "",
      "cost_or_risk": "",
      "tension": ""
    }
  ],
  "perspectives": [
    {
      "lens": "Skeptic",
      "insight": ""
    },
    {
      "lens": "Risk Analyst",
      "insight": ""
    },
    {
      "lens": "Future Self",
      "insight": ""
    },
    {
      "lens": "Outsider",
      "insight": ""
    }
  ],
  "flip_lens": {
    "opposite_perspective": "",
    "what_this_might_reveal": ""
  },
  "questions": [
    "",
    "",
    "",
    "",
    ""
  ],
  "evidence_to_verify": [
    "",
    "",
    ""
  ],
  "what_could_change_my_mind": [
    "",
    "",
    ""
  ]
}
"""


# ============================================================
# GEMINI ANALYSIS
# ============================================================

def get_key():
    key = os.getenv("GEMINI_API_KEY")

    if key:
        return key

    try:
        return st.secrets["GEMINI_API_KEY"]
    except Exception:
        return None


def analyze(payload):
    key = get_key()

    if not key:
        raise RuntimeError(
            "GEMINI_API_KEY is not configured."
        )

    client = genai.Client(api_key=key)

    prompt = (
        SYSTEM_PROMPT
        + "\n\nUSER DECISION CONTEXT:\n"
        + json.dumps(
            payload,
            ensure_ascii=False,
            indent=2
        )
    )

    # Fallback list so temporary model availability
    # problems do not immediately break the demo.
    models = [
        "gemini-3.8-flash",
        "gemini-3.7-flash",
        "gemini-3.6-flash",
        "gemini-3.5-flash",
    ]

    last_error = None

    for model in models:
        try:
            response = client.models.generate_content(
                model=model,
                contents=prompt,
                config={
                    "response_mime_type": "application/json"
                },
            )

            raw = response.text.strip()

            raw = re.sub(
                r"^```(?:json)?\s*|\s*```$",
                "",
                raw
            ).strip()

            result = json.loads(raw)

            return result

        except Exception as e:
            last_error = e
            continue

    raise RuntimeError(
        "All Gemini models are temporarily unavailable. "
        f"Last error: {last_error}"
    )


# ============================================================
# INPUT FORM
# ============================================================

st.markdown("## 🔬 Run a Decision X-Ray")

st.write(
    "Give BlindSpot enough context to challenge your reasoning. "
    "You keep control of the final decision."
)

with st.form("decision_form"):

    decision = st.text_area(
        "What decision are you making?",
        placeholder=(
            "Example: Should I leave my job and start "
            "a business with my friend?"
        ),
        height=100,
    )

    reasoning = st.text_area(
        "Why are you leaning this way?",
        placeholder=(
            "Explain the reasoning that is currently "
            "driving your decision."
        ),
        height=140,
    )

    priorities = st.text_area(
        "What matters most to you?",
        placeholder=(
            "Example: financial stability, growth, "
            "independence, relationships..."
        ),
        height=100,
    )

    uncertainty = st.text_area(
        "What are you unsure about?",
        placeholder=(
            "Mention risks, missing information, "
            "or things you cannot confidently evaluate."
        ),
        height=100,
    )

    category = st.selectbox(
        "Decision category",
        [
            "Career / Work",
            "Education",
            "Business",
            "Finance",
            "Relationships",
            "Health / Lifestyle",
            "Personal",
            "Other",
        ],
    )

    submitted = st.form_submit_button(
        "🔬 Run Decision X-Ray",
        use_container_width=True,
    )


# ============================================================
# RUN ANALYSIS
# ============================================================

if submitted:

    if not decision.strip():
        st.warning("Please enter the decision you are considering.")

    elif not reasoning.strip():
        st.warning("Please explain why you are leaning this way.")

    else:

        payload = {
            "decision": decision.strip(),
            "reasoning": reasoning.strip(),
            "priorities": priorities.strip(),
            "uncertainty": uncertainty.strip(),
            "category": category,
        }

        with st.spinner("Scanning your reasoning for blind spots..."):

            try:
                analysis = analyze(payload)

                st.session_state["analysis"] = analysis
                st.session_state["decision"] = decision.strip()

            except Exception as e:

                st.error(
                    f"AI analysis could not run: {str(e)}"
                )

                st.info(
                    "Set GEMINI_API_KEY locally or add it "
                    "to Streamlit Secrets when deployed."
                )


# ============================================================
# RESULTS
# ============================================================

if "analysis" in st.session_state:

    a = st.session_state["analysis"]

    st.divider()

    st.markdown("## 🔬 X-Ray Results")

    st.markdown(
        f"**Your decision:** "
        f"{st.session_state.get('decision', '')}"
    )

    # --------------------------------------------------------
    # Decision Snapshot
    # --------------------------------------------------------

    snapshot = a.get("decision_snapshot", "")

    if snapshot:
        st.info(snapshot)

    # --------------------------------------------------------
    # Visible Focus
    # --------------------------------------------------------

    st.markdown("### 👁️ What you are seeing")

    visible = a.get("visible_focus", [])

    if visible:

        cols = st.columns(min(3, len(visible)))

        for i, item in enumerate(visible[:3]):

            with cols[i]:

                st.markdown("#### Visible focus")
                st.markdown(item)

    # --------------------------------------------------------
    # Blind Spots
    # --------------------------------------------------------

    st.markdown("### 🕵️ What you might be missing")

    blind_spots = a.get("blind_spots", [])

    if blind_spots:

        cols = st.columns(min(3, len(blind_spots)))

        for i, item in enumerate(blind_spots[:3]):

            with cols[i]:

                st.markdown(
                    f"#### 🔎 {item.get('title', '')}"
                )

                st.markdown(
                    item.get("description", "")
                )

                st.markdown(
                    f"**Why it matters:** "
                    f"{item.get('why_it_matters', '')}"
                )

    # --------------------------------------------------------
    # Hidden Assumptions
    # --------------------------------------------------------

    st.markdown("### 🧠 Hidden assumptions")

    assumptions = a.get("hidden_assumptions", [])

    for item in assumptions:

        st.markdown(
            f"**{item.get('assumption', '')}**"
        )

        status = item.get("status", "")

        if status:
            st.caption(f"Status: {status}")

        question = item.get("question", "")

        if question:
            st.markdown(
                f"*Ask:* {question}"
            )

        st.divider()

    # --------------------------------------------------------
    # Bias Signals
    # --------------------------------------------------------

    st.markdown("### ⚠️ Bias signals")

    biases = a.get("bias_signals", [])

    for item in biases:

        st.markdown(
            f"**{item.get('bias', '')}**"
        )

        st.markdown(
            item.get("signal", "")
        )

        counter_question = item.get(
            "counter_question",
            ""
        )

        if counter_question:

            st.markdown(
                f"*Counter-question:* "
                f"{counter_question}"
            )

        st.divider()

    # --------------------------------------------------------
    # Trade-offs
    # --------------------------------------------------------

    st.markdown(
        "### ⚖️ Trade-offs hiding inside the decision"
    )

    trade = a.get("tradeoffs", [])

    if trade:

        tcols = st.columns(min(3, len(trade)))

        for i, item in enumerate(trade[:3]):

            with tcols[i]:

                st.markdown("#### ⚖️ Trade-off")

                st.markdown(
                    f"**Gain:** "
                    f"{item.get('gain', '')}"
                )

                st.markdown(
                    f"**Cost / risk:** "
                    f"{item.get('cost_or_risk', '')}"
                )

                st.markdown(
                    f"**Tension:** "
                    f"{item.get('tension', '')}"
                )

                st.divider()

    # --------------------------------------------------------
    # Perspective Scan
    # --------------------------------------------------------

    st.markdown("### 🎭 Perspective Scan")

    perspectives = a.get("perspectives", [])

    if perspectives:

        pcols = st.columns(min(4, len(perspectives)))

        for i, item in enumerate(perspectives[:4]):

            with pcols[i]:

                st.markdown(
                    f"#### {item.get('lens', '')}"
                )

                st.markdown(
                    item.get("insight", "")
                )

    # --------------------------------------------------------
    # Flip the Lens
    # --------------------------------------------------------

    st.markdown("### 🔄 Flip the Lens")

    flip = a.get("flip_lens", {})

    opposite = flip.get(
        "opposite_perspective",
        ""
    )

    reveal = flip.get(
        "what_this_might_reveal",
        ""
    )

    if opposite:

        st.markdown(
            "**Try the opposite perspective:**"
        )

        st.markdown(opposite)

    if reveal:

        st.markdown(
            "**What this might reveal:**"
        )

        st.markdown(reveal)

    # --------------------------------------------------------
    # Questions
    # --------------------------------------------------------

    st.markdown("### ❓ Questions worth exploring")

    questions = a.get("questions", [])

    for i, question in enumerate(questions, 1):

        st.markdown(
            f"**{i}.** {question}"
        )

    # --------------------------------------------------------
    # Evidence
    # --------------------------------------------------------

    st.markdown("### 📋 Evidence worth verifying")

    evidence = a.get(
        "evidence_to_verify",
        []
    )

    for item in evidence:

        st.markdown(
            f"- {item}"
        )

    # --------------------------------------------------------
    # What Could Change My Mind
    # --------------------------------------------------------

    st.markdown("### 🧨 What could change your mind?")

    st.caption(
        "These are not predictions. "
        "They are conditions worth identifying before you commit."
    )

    changes = a.get(
        "what_could_change_my_mind",
        []
    )

    for item in changes:

        st.markdown(
            f"- **{item}**"
        )

    # --------------------------------------------------------
    # Footer
    # --------------------------------------------------------

    st.divider()

    st.success(
        "BlindSpot does not choose for you. "
        "It exposes questions, assumptions and missing "
        "context so you can choose more deliberately."
    )

    st.caption(
        "AI output can be incomplete or wrong. "
        "Verify important facts independently."
    )

    st.caption(
        "BlindSpot • Decision X-Ray • Built for PromptWars"
    )
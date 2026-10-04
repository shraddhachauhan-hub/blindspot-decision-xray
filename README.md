# 🧠 BlindSpot — Decision X-Ray

**Don't ask AI what to choose. Ask it what you might be missing.**

BlindSpot is an AI-powered decision-reflection application for PromptWars. It does not recommend an option or make a decision. It audits the reasoning behind a decision and surfaces:

- 👁️ Visible reasoning
- 🕵️ Potential blind spots
- ⚠️ Hidden assumptions
- 🧠 Possible bias signals
- ⚖️ Trade-offs
- 🎭 Multiple perspectives
- 🔄 A “flip the lens” opposite view
- ❓ Questions worth exploring
- 📋 Evidence worth verifying
- 🧨 What could change the user's mind

## Core idea

Most AI decision assistants ask:

> “What should I do?”

BlindSpot asks:

> **“What am I failing to consider?”**

The human remains the decision-maker.

## Tech stack

Python • Streamlit • Google Gemini API (`google-genai`) • GitHub • Streamlit Community Cloud

## Local setup

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:GEMINI_API_KEY="YOUR_KEY"
streamlit run app.py
```

Never commit an API key.

## Streamlit deployment

Push the project to GitHub, create a Streamlit Community Cloud app using `app.py`, and add:

```toml
GEMINI_API_KEY = "YOUR_KEY"
```

to the app's Secrets.

## Suggested demo

Decision:
> Should I leave my job and start a business with my friend?

Reasoning:
> I want independence, the market seems promising, and my friend is talented.

The app should surface questions such as market validation, financial runway, co-founder compatibility, ownership, disagreement handling, and what evidence could change the decision.

## Pitch

> “When people ask AI about a decision, they usually ask ‘What should I do?’ We asked a different question: ‘What am I failing to consider?’ BlindSpot is a Decision X-Ray that uses multiple reasoning lenses to surface assumptions, blind spots, trade-offs and questions — without making the decision for you.”

## Responsible use

BlindSpot is a reflection aid, not professional advice. Important facts should be independently verified.

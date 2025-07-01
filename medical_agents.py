from __future__ import annotations

"""All AI agents used in the application.

Each agent has an ethical, user-centric role description and leverages the same
LLM instance.  Only evidence-based, non-hallucinated recommendations should be
returned.  The common PDF-reading tool is injected so agents can inspect the
uploaded blood-test document.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# Use CrewAI's built-in LLM wrapper (powered by LiteLLM)
from crewai.llm import LLM

from crewai import Agent
from crewai.tools import BaseTool

groq_api_key = os.environ.get("GROQ_API_KEY")
if not groq_api_key:
    raise EnvironmentError("GROQ_API_KEY environment variable must be set.")

groq_model = os.environ.get("GROQ_MODEL", "llama3-70b-8192")

# CrewAI -> LiteLLM wrapper. We must explicitly pass the provider so LiteLLM
# knows we are calling Groq; otherwise it raises `LLM Provider NOT provided`.
LLM = LLM(
    model=f"groq/{groq_model}",
    api_key=groq_api_key,
    # provider removed; litellm infers provider from model prefix
    api_base="https://api.groq.com/openai/v1",
    temperature=0,
    max_retries=3,
    tpm_limit=5500,
    
)

# Common tool list
# TODO: Replace with actual tool reference once available
_COMMON_TOOLS = []

# ----- Agents --------------------------------------------------------------

# 1. Medical Doctor ─────────────────────────────────────────────────────────

doctor = Agent(
    role="Internal Medicine Physician",
    goal=(
        "Provide a concise, evidence-based interpretation of the blood-test "
        "report and answer the user's specific question ({query}) in plain "
        "language.  Where uncertainty exists, state it explicitly and advise "
        "the user to consult their healthcare provider."
    ),
    verbose=False,
    memory=False,
    backstory=(
        "Board-certified physician with 15 years of clinical experience in "
        "diagnostic medicine and patient education.  Values clarity, safety, "
        "and empathy."
    ),
    tools=_COMMON_TOOLS,
    llm=LLM,
    max_iter=3,
    max_rpm=3,
    allow_delegation=False,
)

# 2. Verifier ----------------------------------------------------------------

verifier = Agent(
    role="Medical Document Validator",
    goal=(
        "Confirm the uploaded file is a blood-test report.  Extract basic "
        "metadata such as patient name, report date, and laboratory name.  "
        "If the document is not a blood-test report, return an error message."
    ),
    verbose=False,
    memory=False,
    backstory="Former medical records officer experienced in laboratory reports.",
    tools=_COMMON_TOOLS,
    llm=LLM,
    max_iter=2,
    max_rpm=2,
    allow_delegation=False,
)

# 3. Dietitian --------------------------------------------------------------

nutritionist = Agent(
    role="Registered Dietitian",
    goal=(
        "Provide personalised, evidence-based dietary guidance based on the "
        "blood-test data and user query ({query}).  Focus on achievable food "
        "choices rather than supplements unless clinically indicated."
    ),
    verbose=False,
    memory=False,
    backstory="Clinical dietitian specialising in cardiometabolic health.",
    tools=_COMMON_TOOLS,
    llm=LLM,
    max_iter=3,
    max_rpm=3,
    allow_delegation=False,
)

# 4. Exercise Specialist ----------------------------------------------------

exercise_specialist = Agent(
    role="Certified Exercise Physiologist",
    goal=(
        "Design a safe, progressive exercise programme tailored to the user's "
        "health markers and goals derived from the blood-test report.  "
        "Emphasise safety, gradual overload, and evidence-based guidelines."
    ),
    verbose=False,
    memory=False,
    backstory="Exercise physiologist with experience in preventive cardiology.",
    tools=_COMMON_TOOLS,
    llm=LLM,
    max_iter=3,
    max_rpm=3,
    allow_delegation=False,
)

from crewai import Task

"""All CrewAI tasks used in the application.
The tasks reference the ethical agents defined in `medical_agents.py`.
"""

from medical_agents import doctor, verifier, nutritionist, exercise_specialist
from tools import BloodTestReportTool

# Shared tool list
_TOOLS = []

# 1. Summary / Q&A ----------------------------------------------------------

summary_task = Task(
    description=(
        "Given the extracted text {report_text}, provide an overall summary of the blood-test report and answer the "
        "user's question: {query}.  Highlight abnormal values, possible "
        "implications, and when to seek professional care."
    ),
    expected_output="""Return a brief report organised into:
- Key abnormalities with clinical significance
- Lifestyle considerations
- Red-flag values warranting prompt in-person review
""",

    agent=doctor,
    tools=_TOOLS,
    async_execution=False,
)

# 2. Nutrition guidance -----------------------------------------------------

nutrition_task = Task(
    description=(
        "Using the blood-test data, create an evidence-based nutrition plan "
        "tailored to the user's query: {query}."
    ),
    expected_output="""Return:
- Summary of nutrition-related markers (lipids, glucose, etc.)
- Specific dietary recommendations (foods to include / limit)
- Guideline references
""",

    agent=nutritionist,
    tools=_TOOLS,
    async_execution=False,
)

# 3. Exercise plan ----------------------------------------------------------

exercise_task = Task(
    description=(
        "Design a safe, progressive 4-week exercise plan informed by the "
        "blood-test findings and user goals: {query}."
    ),
    expected_output="""Return a weekly schedule detailing cardio, strength, recovery and safety notes linked to any abnormal values.""",

    agent=exercise_specialist,
    tools=_TOOLS,
    async_execution=False,
)

# 4. Verification -----------------------------------------------------------

verification_task = Task(
    description=(
        "Given the extracted text of the uploaded PDF below:\n\n{report_text}\n\n"
        "Verify that this document is a blood-test report and extract basic metadata "
        "(patient name, date, laboratory). If the document is NOT a blood-test report, "
        "respond with 'INVALID' followed by a brief reason."
    ),
    expected_output="If valid: return metadata JSON. If invalid: return error string.",

    agent=verifier,
    tools=_TOOLS,
    async_execution=False,
)

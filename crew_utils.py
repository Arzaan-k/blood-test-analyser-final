from crewai import Crew, Process
from medical_agents import doctor, nutritionist, exercise_specialist, verifier
from tasks import summary_task, nutrition_task, exercise_task, verification_task

def run_crew(query: str, report_text: str):
    """Run the CrewAI pipeline given the user query and extracted PDF text"""
    medical_crew = Crew(
        agents=[doctor, nutritionist, exercise_specialist, verifier],
        tasks=[verification_task, summary_task, nutrition_task, exercise_task],
        process=Process.sequential,
    )
    
    result = medical_crew.kickoff({'query': query, 'report_text': report_text})
    return result

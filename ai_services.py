import os
from google import genai
from dotenv import load_dotenv

load_dotenv()
client = genai.Client(api_key=os.getenv(AIzaSyBKHQ21I92s19VYI2ieVz6cd1Ns5vkbfbs))

def summarize_meeting(content: str):
    prompt = f"Summarize these meeting notes and list key decisions: {content}"
    response = client.models.generate_content(
        model="gemini-2.0-flash", 
        contents=prompt
    )
    return response.text

# ai_services.py
def analyze_meeting_health(content: str):
    prompt = f"""Analyze the following meeting notes for emotional health and risks:
    - Identify unresolved questions.
    - Identify any conflicting viewpoints or tension.
    - Rate overall sentiment (Positive/Neutral/Negative).
    If there are major unresolved issues, tag it as 'High-Risk'.
    Notes: {content}"""
    
    response = client.models.generate_content(model="gemini-1.5-flash", contents=prompt)
    return response.text
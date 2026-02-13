import os
from google import genai
from dotenv import load_dotenv

load_dotenv()
# Pass the string name of the variable to getenv, not the key itself
GEMINI_KEY = os.getenv("GOOGLE_API_KEY") 
client = genai.Client(api_key=GEMINI_KEY)

def analyze_meeting_sentiment(content: str):
    # Added explicit instruction to return raw JSON to avoid parsing errors
    prompt = f"""
    Act as a corporate analyst. Analyze these meeting notes:
    '{content}'
    
    Return ONLY a raw JSON response (no markdown blocks) with:
    1. sentiment: (Positive/Neutral/Negative)
    2. risk_level: (High/Medium/Low) - Set to High if there are unresolved conflicts.
    3. summary: A 2-sentence summary of the tone.
    """
    response = client.models.generate_content(
        model="gemini-2.0-flash", 
        contents=prompt
    )
    return response.text
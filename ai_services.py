import os
import json
from google import genai
from dotenv import load_dotenv

load_dotenv()

GEMINI_KEY = os.getenv("GOOGLE_API_KEY")
if not GEMINI_KEY:
    raise ValueError("GOOGLE_API_KEY not set in environment")

client = genai.Client(api_key=GEMINI_KEY)


def analyze_meeting_sentiment(content: str):
    prompt = f"""
    Analyze the following meeting notes:

    {content}

    Return ONLY valid JSON with:
    sentiment: Positive/Neutral/Negative
    risk_level: High/Medium/Low
    summary: 2 sentence summary
    """

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt
    )

    try:
        return json.loads(response.text)
    except:
        return {"error": "AI response parsing failed", "raw": response.text}

# app/chatroom/gemini.py

import google.generativeai as genai
from app.config import settings

genai.configure(api_key=settings.GEMINI_API_KEY)

model = genai.GenerativeModel("gemini-2.0-flash")

def call_gemini_api(user_message: str) -> str:
    try:
        response = model.generate_content(user_message)
        return response.text.strip()
    except Exception as e:
        return f"Gemini error: {str(e)}"

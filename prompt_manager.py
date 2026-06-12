# prompt_manager.py
import json
import mimetypes
from datetime import datetime
from google import genai
from google.genai import types
from rotation import get_next_api_key, MODELS

class PromptManager:
    def __init__(self):
        pass

    def enhance_prompt(self, raw_prompt, file_name=None, mode="ai", memory_context=""):
        current_time = datetime.now().strftime("%I:%M %p, %A, %B %d, %Y")
        
        # Categorization Logic ka System Prompt
        system_instruction = f"""
        You are an advanced Intent Classifier and Prompt Engineer.
        Current Time: {current_time}
        Memory: {memory_context}
        Raw Input: {raw_prompt}

        TASK: 
        1. Classify the user query into exactly ONE category: 'Greetings', 'Religious_Studies' (Quran/Hadees), 'Coding', 'General', or 'File_Analysis'.
        2. Based on the category, generate an optimized master prompt.
        3. ALWAYS respond in Hinglish.
        4. If it's 'Religious_Studies', ensure the tone is respectful and accurate.

        Respond ONLY in this JSON format:
        {{"category": "Category_Name", "enhanced_prompt": "..."}}
        """

        for attempt in range(3):
            try:
                api_key = get_next_api_key()
                client = genai.Client(api_key=api_key)
                model_name = MODELS[attempt % len(MODELS)]
                
                response = client.models.generate_content(
                    model=model_name,
                    contents=system_instruction,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        temperature=0.2
                    )
                )
                
                result = json.loads(response.text)
                return {
                    "category": result.get("category", "General"),
                    "enhanced_prompt": result.get("enhanced_prompt", raw_prompt)
                }
            except Exception:
                continue

        return {"category": "General", "enhanced_prompt": raw_prompt}
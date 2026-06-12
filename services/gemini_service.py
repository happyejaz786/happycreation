# services/gemini_service.py

import os
from google import genai
from google.genai import types
from services.search_service import SearchService
from rotation import get_next_api_key, MODELS

class GeminiService:
    def __init__(self):
        self.search_service = SearchService()
        self.MODELS = MODELS

    def _get_client(self):
        api_key = get_next_api_key()
        return genai.Client(api_key=api_key)

    def generate_response(self, enhanced_prompt, file_path=None, mode="ai"):
        final_prompt = f"{enhanced_prompt}\n\nNote: Always respond in Hinglish. If you generate code, ALWAYS enclose it in triple backticks (```) for easy copying."
        
        # Multimodal payload setup
        contents = [final_prompt]
        
        # Agar image file hai, toh use content list mein add karo
        if file_path and os.path.exists(file_path):
            try:
                # File upload via SDK
                client = self._get_client()
                uploaded_file = client.files.upload(path=file_path)
                contents.append(uploaded_file)
            except Exception as e:
                print(f"DEBUG: File upload failed: {e}")

        for model in self.MODELS:
            try:
                client = self._get_client()
                response = client.models.generate_content(
                    model=model,
                    contents=contents
                )

                if response and response.text:
                    return {
                        "success": True,
                        "response": response.text,
                        "model": model,
                        "mode": mode
                    }
            except Exception as e:
                print(f"DEBUG: Model {model} failed: {e}")
                continue

        return {
            "success": False,
            "response": "क्षमा करें, सभी मॉडल्स और कीज़ पर रिक्वेस्ट विफल रही।",
            "mode": mode
        }
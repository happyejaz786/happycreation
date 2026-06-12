# services/search_service.py

from ddgs import DDGS
from googleapiclient.discovery import build
import os

class SearchService:
    AI_MODE = "ai"
    WEB_MODE = "web"

    def __init__(self):
        self.google_api_key = os.getenv("GOOGLE_SEARCH_API_KEY")
        self.google_cx_id = os.getenv("GOOGLE_CX_ID")
        self.google_active = True  # Google API Status Flag

    def search_web(self, query: str, max_results: int = 5):
        # Google API को हमेशा के लिए हटा दिया
        print(f"[SEARCH] Using DDGS for: {query}")
        ddgs_data = self._search_ddgs(query, max_results)
        return {
            "results": ddgs_data,
            "source": "Powered by DuckDuckGo"
        }
    
    def _search_ddgs(self, query: str, max_results: int):
        results = []
        try:
            with DDGS() as ddgs:
                search_results = ddgs.text(query, max_results=max_results)
                for item in search_results:
                    results.append({
                        "title": item.get("title", ""),
                        "body": item.get("body", ""),
                        "url": item.get("href", "")
                    })
        except Exception as e:
            print(f"[DDGS SEARCH ERROR]: {str(e)}")
        return results

    def build_search_context(self, results):
        if not results:
            return ""
        context = []
        for idx, item in enumerate(results, start=1):
            context.append(f"Source {idx}\nTitle: {item['title']}\nContent: {item['body']}\nURL: {item['url']}\n")
        return "\n".join(context)

    def build_final_prompt(self, original_prompt, web_context):
        return f"{original_prompt}\n\nSearch Results:\n{web_context}"

    def get_mode_label(self, mode):
        return "Web Search Mode" if mode == self.WEB_MODE else "AI Mode"
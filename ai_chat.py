# routes/ai_chat.py

import json
import uuid

from fastapi import APIRouter, Request, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from prompt_manager import PromptManager

from services.history_service import HistoryService
from services.upload_service import UploadService
from services.search_service import SearchService
from services.gemini_service import GeminiService

router = APIRouter()

DB_FILE = "happy_agent.db"

prompt_manager = PromptManager()
history_service = HistoryService(DB_FILE)
upload_service = UploadService()
search_service = SearchService()
gemini_service = GeminiService()


class HistoryAction(BaseModel):
    id: str
    title: str | None = None


# ==========================================
# HISTORY
# ==========================================

@router.get("/history")
async def get_history():

    chats = history_service.get_chat_history()

    return JSONResponse(content=chats)


@router.get("/get_chat_details/{chat_id}")
async def get_chat_details(chat_id: str):

    messages = history_service.get_chat_details(
        chat_id
    )

    return JSONResponse(
        content={
            "status": "success",
            "history": messages
        }
    )


@router.post("/history/pin")
async def pin_chat(payload: HistoryAction):

    history_service.pin_chat(
        payload.id,
        True
    )

    return JSONResponse(
        content={
            "status": "success"
        }
    )


@router.post("/history/rename")
async def rename_chat(payload: HistoryAction):

    history_service.rename_chat(
        payload.id,
        payload.title
    )

    return JSONResponse(
        content={
            "status": "success"
        }
    )


@router.post("/history/delete")
async def delete_chat(payload: HistoryAction):

    history_service.delete_chat(
        payload.id
    )

    return JSONResponse(
        content={
            "status": "success"
        }
    )


# ==========================================
# MAIN CHAT
# ==========================================

@router.post("/smart_chat")
async def smart_chat(request: Request, background_tasks: BackgroundTasks):

    try:

        form_data = await request.form()

        message = str(
            form_data.get(
                "message",
                ""
            )
        ).strip()

        chat_id = str(
            form_data.get(
                "chat_id",
                ""
            )
        ).strip()

        mode = str(
            form_data.get(
                "mode",
                "ai"
            )
        ).lower()
        print(f"MODE RECEIVED: {mode}")

        uploaded_files = form_data.getlist(
            "files"
        )

        saved_files = []

        if uploaded_files:

            saved_files = await upload_service.save_files(uploaded_files)
        
        file_path = saved_files[0].get("path") if saved_files else None

        if not message and not saved_files:

            return JSONResponse(
                status_code=400,
                content={
                    "status": "error",
                    "message":
                    "Message or file required."
                }
            )

        primary_file = None

        if saved_files:
            primary_file = (saved_files[0].get("original_name"))

        # --- 1. Fetch Memory Context ---
        memory_context = ""
        if chat_id:
            try:
                memory_context = history_service.get_summary(chat_id)
            except AttributeError:
                pass # Safe fallback in case method is missing in history_service

        # --- 2. Pass memory_context to prompt_manager ---
        prompt_data = prompt_manager.enhance_prompt(
            raw_prompt=message if message else "Analyze uploaded file",
            file_name=primary_file,
            mode=mode,
            memory_context=memory_context 
        )

        enhanced_prompt = (
            prompt_data[
                "enhanced_prompt"
            ]
        )

        # --- Search Service Block (Untouched) ---
        source_indicator = "" 
        if mode == search_service.WEB_MODE:
            search_results = search_service.search_web(message)
            results = search_results.get("results", [])
            source_indicator = search_results.get("source", "")
            
            web_context = search_service.build_search_context(results)
            enhanced_prompt = search_service.build_final_prompt(
                enhanced_prompt, 
                web_context
            )

        # --- Gemini Service Block ---
        response_data = gemini_service.generate_response(
            enhanced_prompt=enhanced_prompt,
            file_path=file_path,
            mode=mode
        )
        
        if not response_data["success"]:
            return JSONResponse(
                status_code=500,
                content={"status": "error", "message": response_data.get("error", "Unknown Error")}
            )

        reply = response_data["response"]

        # --- Save Chat History ---
        if not chat_id:
            chat_id = (
                history_service
                .create_chat(
                    title=
                    message[:30]
                    if message
                    else "File Analysis"
                )
            )
        history_service.save_message(
            chat_id,
            "user",
            message
            if message
            else "Uploaded file"
        )

        history_service.save_message(chat_id, "assistant", reply)

        # --- 3. Background Task Execution ---
        try:
            background_tasks.add_task(history_service.generate_and_update_cognitive_summary, chat_id)
        except AttributeError:
            pass # Safe fallback

        upload_message = None

        if saved_files:

            upload_message = (
                upload_service
                .get_upload_message(
                    saved_files
                )
            )

        return JSONResponse(
            content={
                "status": "success",
                "chat_id": chat_id,
                "reply": reply,
                "source_indicator": source_indicator,
                "mode": mode,
                "mode_label": search_service.get_mode_label(mode),
                "category": prompt_data["category"],
                "prompt_used": enhanced_prompt,
                "upload_message": upload_message,
                "files": saved_files
            }
        )
    except Exception as e:
        import traceback
        print(f"DEBUG ERROR: {traceback.format_exc()}")
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": str(e)
            }
        )
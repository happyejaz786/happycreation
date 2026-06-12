# services/upload_service.py

import os
import uuid
from pathlib import Path
from datetime import datetime


class UploadService:

    ALLOWED_EXTENSIONS = {
        # Documents
        "pdf", "doc", "docx", "txt", "csv", "xlsx",

        # Images
        "jpg", "jpeg", "png", "gif", "webp",

        # Audio
        "mp3", "wav", "m4a"
    }

    BLOCKED_EXTENSIONS = {
        "exe", "bat", "dll", "cmd", "msi"
    }

    def __init__(self, upload_root="static/uploads"):
        self.upload_root = upload_root

        self.images_dir = os.path.join(upload_root, "images")
        self.documents_dir = os.path.join(upload_root, "documents")
        self.audio_dir = os.path.join(upload_root, "audio")
        self.temp_dir = os.path.join(upload_root, "temp")

        self._create_directories()

    # --------------------------------------------------
    # Folder Creation
    # --------------------------------------------------

    def _create_directories(self):
        Path(self.images_dir).mkdir(parents=True, exist_ok=True)
        Path(self.documents_dir).mkdir(parents=True, exist_ok=True)
        Path(self.audio_dir).mkdir(parents=True, exist_ok=True)
        Path(self.temp_dir).mkdir(parents=True, exist_ok=True)

    # --------------------------------------------------
    # Validation
    # --------------------------------------------------

    def validate_file(self, filename):
        extension = filename.rsplit(".", 1)[-1].lower()

        if extension in self.BLOCKED_EXTENSIONS:
            return False

        return extension in self.ALLOWED_EXTENSIONS

    # --------------------------------------------------
    # File Type Routing
    # --------------------------------------------------

    def get_target_directory(self, filename):
        extension = filename.rsplit(".", 1)[-1].lower()

        if extension in {
            "jpg", "jpeg", "png", "gif", "webp"
        }:
            return self.images_dir

        if extension in {
            "mp3", "wav", "m4a"
        }:
            return self.audio_dir

        return self.documents_dir

    # --------------------------------------------------
    # Safe Filename
    # --------------------------------------------------

    def generate_safe_filename(self, filename):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = uuid.uuid4().hex[:8]

        clean_name = os.path.basename(filename)

        return f"{timestamp}_{unique_id}_{clean_name}"

    # --------------------------------------------------
    # Save Multiple Files
    # --------------------------------------------------

    async def save_files(self, files):

        uploaded_files = []

        for file in files:

            if not file.filename:
                continue

            if not self.validate_file(file.filename):
                continue

            target_dir = self.get_target_directory(file.filename)

            safe_filename = self.generate_safe_filename(
                file.filename
            )

            file_path = os.path.join(
                target_dir,
                safe_filename
            )

            content = await file.read()

            with open(file_path, "wb") as f:
                f.write(content)

            uploaded_files.append({
                "original_name": file.filename,
                "saved_name": safe_filename,
                "path": file_path,
                "size": len(content)
            })

        return uploaded_files

    # --------------------------------------------------
    # Floating Message
    # --------------------------------------------------

    def get_upload_message(self, uploaded_files):

        count = len(uploaded_files)

        if count == 0:
            return "❌ Upload failed"

        if count == 1:
            return (
                f"📎 "
                f"{uploaded_files[0]['original_name']} "
                f"attached successfully"
            )

        return f"📎 {count} files attached successfully"

    # --------------------------------------------------
    # Response Builder
    # --------------------------------------------------

    def build_response(self, uploaded_files):

        return {
            "success": len(uploaded_files) > 0,
            "message": self.get_upload_message(
                uploaded_files
            ),
            "files": uploaded_files
        }
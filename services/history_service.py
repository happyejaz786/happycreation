# services/history_service.py
import sqlite3
import uuid
from datetime import datetime
# Import genai to generate summary
from google import genai
from rotation import get_next_api_key, MODELS

class HistoryService:
    def __init__(self, db_file):
        self.db_file = db_file
        self._initialize_database()

    def _get_connection(self):
        conn = sqlite3.connect(self.db_file)
        conn.row_factory = sqlite3.Row
        return conn

    '''def _initialize_database(self):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS chats (id TEXT PRIMARY KEY, title TEXT, pinned INTEGER, created_at TEXT, updated_at TEXT, summary TEXT)")
        cursor.execute("CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY AUTOINCREMENT, chat_id TEXT, role TEXT, content TEXT, created_at TEXT, FOREIGN KEY(chat_id) REFERENCES chats(id))")
        conn.commit()
        conn.close()'''
    def _initialize_database(self):
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # 1. Pehle table banayein (agar nahi bani hai)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chats (
                id TEXT PRIMARY KEY, 
                title TEXT, 
                pinned INTEGER, 
                created_at TEXT, 
                updated_at TEXT, 
                summary TEXT, 
                category TEXT
            )
        """)
        
        # 2. Check karein ki 'summary' aur 'category' column exist karte hain ya nahi
        # Agar nahi karte, toh unhe add karein
        try:
            cursor.execute("ALTER TABLE chats ADD COLUMN summary TEXT")
        except sqlite3.OperationalError:
            pass # Column already exists
            
        try:
            cursor.execute("ALTER TABLE chats ADD COLUMN category TEXT")
        except sqlite3.OperationalError:
            pass # Column already exists

        # Messages table waisi hi rahegi
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                chat_id TEXT, 
                role TEXT, 
                content TEXT, 
                created_at TEXT, 
                FOREIGN KEY(chat_id) REFERENCES chats(id)
            )
        """)
        
        conn.commit()
        conn.close()

    def get_summary(self, chat_id):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT summary FROM chats WHERE id = ?", (chat_id,))
        row = cursor.fetchone()
        conn.close()
        return row["summary"] if row and row["summary"] else ""

    '''def generate_and_update_cognitive_summary(self, chat_id):
        """Background task to update chat memory using FULL history."""
        messages = self.get_chat_details(chat_id)
        if not messages: return

        # Limit hatakar poori history ka context liya
        full_context = "\n".join([f"{m['role']}: {m['content']}" for m in messages])
        
        try:
            client = genai.Client(api_key=get_next_api_key())
            # Prompt mein clearly bola ki POORI chat summary banaye
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=f"Summarize the ENTIRE chat history below for cognitive memory context (keep it concise but comprehensive): \n\n{full_context}"
            )
            summary = response.text
            
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE chats SET summary = ? WHERE id = ?", (summary, chat_id))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"DEBUG: Full history summary generation failed: {e}")'''
    
    def generate_and_update_cognitive_summary(self, chat_id):
        """Background task to update chat memory using FULL history and dynamic models."""
        messages = self.get_chat_details(chat_id)
        if not messages: return

        full_context = "\n".join([f"{m['role']}: {m['content']}" for m in messages])
        for model in MODELS:
            try:
                client = genai.Client(api_key=get_next_api_key())
                response = client.models.generate_content(
                    model=model, # Ab ye dynamic hai
                    contents=f"Summarize the ENTIRE chat history below for cognitive memory context. Always respond in Hinglish: \n\n{full_context}"
                )
                summary = response.text
                conn = self._get_connection()
                cursor = conn.cursor()
                cursor.execute("UPDATE chats SET summary = ? WHERE id = ?", (summary, chat_id))
                conn.commit()
                conn.close()
                return # Summary success, exit loop
            except Exception as e:
                print(f"DEBUG: Summary failed with {model}: {e}")
                continue
    # ... (बाकी आपके पुराने ऑपरेशन्स save_message, create_chat आदि यहाँ रहेंगे)
    def create_chat(self, title="New Chat"):
        chat_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO chats (id, title, pinned, created_at, updated_at) VALUES (?, ?, ?, ?, ?)", (chat_id, title, 0, now, now))
        conn.commit()
        conn.close()
        return chat_id

    def get_chat_details(self, chat_id):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM messages WHERE chat_id = ? ORDER BY id ASC", (chat_id,))
        messages = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return messages

    def save_message(self, chat_id, role, content):
        now = datetime.utcnow().isoformat()
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO messages (chat_id, role, content, created_at) VALUES (?, ?, ?, ?)", (chat_id, role, content, now))
        cursor.execute("UPDATE chats SET updated_at = ? WHERE id = ?", (now, chat_id))
        conn.commit()
        conn.close()
        
    def get_chat_history(self):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, title, created_at FROM chats ORDER BY updated_at DESC")
        chats = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return chats
        
    def update_chat_category(self, chat_id, category):
        conn = self._get_connection()
        cursor = conn.cursor()
        # Humne 'chats' table mein 'category' column add kiya hai (ya kar lein)
        cursor.execute("UPDATE chats SET category = ? WHERE id = ?", (category, chat_id))
        conn.commit()
        conn.close()
        
    def delete_chat(self, chat_id):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM messages WHERE chat_id = ?", (chat_id,))
        cursor.execute("DELETE FROM chats WHERE id = ?", (chat_id,))
        conn.commit()
        conn.close()

    def get_chat_history(self):
        conn = self._get_connection()
        cursor = conn.cursor()
        # summary aur category select karein agar zaroorat ho
        cursor.execute("SELECT id, title, created_at, category FROM chats ORDER BY updated_at DESC")
        chats = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return chats
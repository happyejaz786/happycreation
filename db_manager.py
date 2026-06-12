# db_manager.py
import sqlite3
from datetime import datetime
from rotation import get_client_and_model

class DatabaseManager:
    def __init__(self, db_path="happy_agent.db"):
        self.db_path = db_path
        self._init_db()

    def _get_connection(self):
        return sqlite3.connect(self.db_path, check_same_thread=False)

    def _init_db(self):
        """
        Database initialization and schema upgrade.
        Safely adds the 'summary' column to existing chats table.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Create core tables if they don't exist
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS chats (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    pinned INTEGER DEFAULT 0,
                    created_at TEXT,
                    updated_at TEXT
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    chat_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TEXT,
                    FOREIGN KEY(chat_id) REFERENCES chats(id)
                )
            ''')
            
            # Dynamic Schema Upgrade: Add 'summary' column for Cognitive Memory
            try:
                cursor.execute("ALTER TABLE chats ADD COLUMN summary TEXT")
            except sqlite3.OperationalError:
                # OperationalError means column already exists, which is perfectly fine.
                pass
            
            conn.commit()

    def save_message(self, chat_id, role, content):
        """Saves a new message to the database."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            now = datetime.now().isoformat()
            
            # Ensure the chat session exists
            cursor.execute("INSERT OR IGNORE INTO chats (id, title, created_at, updated_at) VALUES (?, ?, ?, ?)", 
                           (chat_id, "New Cognitive Chat", now, now))
            
            # Insert the actual message
            cursor.execute('''
                INSERT INTO messages (chat_id, role, content, created_at)
                VALUES (?, ?, ?, ?)
            ''', (chat_id, role, content, now))
            
            # Update chat's last updated time
            cursor.execute("UPDATE chats SET updated_at = ? WHERE id = ?", (now, chat_id))
            conn.commit()

    def get_recent_context(self, chat_id, limit=6):
        """Fetches the most recent messages to maintain direct flow."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT role, content FROM messages 
                WHERE chat_id = ? ORDER BY id DESC LIMIT ?
            ''', (chat_id, limit))
            # Reverse to maintain chronological order for the AI
            messages = [{"role": row[0], "content": row[1]} for row in cursor.fetchall()][::-1]
            return messages

    def get_summary(self, chat_id):
        """Retrieves the permanent cognitive memory (summary) of the chat."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT summary FROM chats WHERE id = ?", (chat_id,))
            result = cursor.fetchone()
            return result[0] if result and result[0] else ""

    def update_summary(self, chat_id, summary_text):
        """Updates the permanent summary in the database."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE chats SET summary = ? WHERE id = ?", (summary_text, chat_id))
            conn.commit()

    async def generate_and_update_cognitive_summary(self, chat_id):
        """
        The Brain Logic: Fetches full chat history, sends it to AI for summarization,
        and saves the condensed essence back to the DB.
        """
        # Fetching a large chunk of history for global context
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT role, content FROM messages WHERE chat_id = ? ORDER BY id ASC', (chat_id,))
            all_messages = cursor.fetchall()

        if not all_messages:
            return ""

        # Format history for the AI to read
        chat_text = "\n".join([f"{row[0]}: {row[1]}" for row in all_messages])
        current_summary = self.get_summary(chat_id)

        # Prompt specifically designed for internal summarization
        summarization_prompt = f"""
        You are the Background Memory Optimizer for an AI Agent.
        Your task is to analyze the entire chat history and extract the core essence, user preferences, ongoing tasks, and important facts.
        
        Previous Summary Context: {current_summary}
        
        Full Chat History:
        {chat_text}
        
        Instructions:
        1. Create a highly concise, updated summary in bullet points (maximum 5 points).
        2. Focus ONLY on what the AI needs to remember to help the user effectively in future turns.
        3. Do not include pleasantries. Return ONLY the bullet points.
        """

        try:
            client, model_name = get_client_and_model() # Using your rotation logic
            response = client.models.generate_content(
                model=model_name,
                contents=summarization_prompt
            )
            
            new_summary = response.text.strip()
            self.update_summary(chat_id, new_summary)
            return new_summary
            
        except Exception as e:
            print(f"⚠️ Memory Summarization Error: {e}")
            return current_summary
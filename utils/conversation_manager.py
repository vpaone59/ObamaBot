"""
Conversation manager for AI chat memory and user tracking.
Handles conversation history persistence and user customizations with PostgreSQL.
"""

from datetime import UTC, datetime, timedelta

import psycopg2

from .db_helper import get_database_connection, return_database_connection
from .logging_config import create_new_logger

logger = create_new_logger(__name__)

# Configuration
MAX_CONVERSATION_HISTORY = 15  # Keep last 15 messages per user
CONVERSATION_WINDOW_HOURS = 24  # Only include messages from last 24 hours


class ConversationManager:
    """Manages conversation history and user tracking for AI memory."""

    @staticmethod
    def get_or_create_user(
        discord_id: int, display_name: str, custom_nickname: str | None = None
    ) -> dict:
        """
        Get or create a user record. Returns user data including custom nickname if set.

        Args:
            discord_id: Discord user ID
            display_name: Current Discord display name
            custom_nickname: Optional custom nickname (e.g., "Daddy Paul")

        Returns:
            dict with discord_id, display_name, custom_nickname, created_at
        """
        try:
            conn = get_database_connection()
            cursor = conn.cursor()

            # Try to get existing user
            cursor.execute(
                "SELECT discord_id, display_name, custom_nickname FROM users WHERE discord_id = %s",
                (discord_id,),
            )
            row = cursor.fetchone()

            if row:
                user = {
                    "discord_id": row[0],
                    "display_name": row[1],
                    "custom_nickname": row[2],
                }
                # Update display name if changed
                if row[1] != display_name:
                    cursor.execute(
                        "UPDATE users SET display_name = %s, updated_at = CURRENT_TIMESTAMP WHERE discord_id = %s",
                        (display_name, discord_id),
                    )
                    conn.commit()
                    user["display_name"] = display_name

                cursor.close()
                return_database_connection(conn)
                return user
            else:
                # Create new user
                cursor.execute(
                    "INSERT INTO users (discord_id, display_name, custom_nickname) VALUES (%s, %s, %s)",
                    (discord_id, display_name, custom_nickname),
                )
                conn.commit()
                user = {
                    "discord_id": discord_id,
                    "display_name": display_name,
                    "custom_nickname": custom_nickname,
                }
                logger.info(
                    "Created new user record | Discord ID: %s | Name: %s",
                    discord_id,
                    display_name,
                )
                cursor.close()
                return_database_connection(conn)
                return user

        except psycopg2.Error as e:
            logger.error("Database error in get_or_create_user: %s", e)
            return {
                "discord_id": discord_id,
                "display_name": display_name,
                "custom_nickname": custom_nickname,
            }

    @staticmethod
    def add_message_to_history(discord_id: int, role: str, content: str) -> bool:
        """
        Add a message to conversation history.

        Args:
            discord_id: Discord user ID
            role: "user" or "assistant"
            content: Message content

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            conn = get_database_connection()
            cursor = conn.cursor()

            cursor.execute(
                "INSERT INTO conversations (discord_id, role, content) VALUES (%s, %s, %s)",
                (discord_id, role, content),
            )
            conn.commit()
            cursor.close()
            return_database_connection(conn)
            logger.debug(
                "Message added to history | User: %s | Role: %s | Length: %d",
                discord_id,
                role,
                len(content),
            )
            return True

        except psycopg2.Error as e:
            logger.error("Database error adding message to history: %s", e)
            return False

    @staticmethod
    def get_conversation_history(discord_id: int) -> list:
        """
        Get recent conversation history for a user.

        Returns:
            list of dicts with keys: role, content, created_at
        """
        try:
            conn = get_database_connection()
            cursor = conn.cursor()

            # Get messages from last 24 hours, limited to MAX_CONVERSATION_HISTORY
            cutoff_time = (
                datetime.now(tz=UTC) - timedelta(hours=CONVERSATION_WINDOW_HOURS)
            ).isoformat()

            cursor.execute(
                """
                SELECT role, content, created_at 
                FROM conversations 
                WHERE discord_id = %s AND created_at > %s
                ORDER BY created_at DESC
                LIMIT %s
                """,
                (discord_id, cutoff_time, MAX_CONVERSATION_HISTORY),
            )

            rows = cursor.fetchall()
            cursor.close()
            return_database_connection(conn)

            # Reverse to chronological order (oldest first)
            history = [
                {"role": row[0], "content": row[1], "created_at": row[2]}
                for row in reversed(rows)
            ]

            logger.debug(
                "Retrieved conversation history | User: %s | Messages: %d",
                discord_id,
                len(history),
            )
            return history

        except psycopg2.Error as e:
            logger.error("Database error retrieving conversation history: %s", e)
            return []

    @staticmethod
    def format_history_for_context(history: list, user_name: str) -> str:
        """
        Format conversation history into a context string for the AI.

        Args:
            history: List of message dicts from get_conversation_history
            user_name: Name of the current user

        Returns:
            Formatted context string
        """
        if not history:
            return ""

        context_lines = ["## Recent Conversation Context", ""]

        for msg in history:
            role = "You" if msg["role"] == "assistant" else user_name
            # Truncate long messages for context
            content = msg["content"]
            if len(content) > 300:
                content = content[:300] + "..."

            context_lines.append(f"**{role}**: {content}")

        context_lines.append("")
        return "\n".join(context_lines)

    @staticmethod
    def clear_old_conversations(hours: int = 72) -> int:
        """
        Delete conversation history older than specified hours.
        Useful for maintenance and privacy.

        Args:
            hours: Delete messages older than this many hours

        Returns:
            Number of rows deleted
        """
        try:
            conn = get_database_connection()
            cursor = conn.cursor()

            cutoff_time = (datetime.now(tz=UTC) - timedelta(hours=hours)).isoformat()

            cursor.execute(
                "DELETE FROM conversations WHERE created_at < %s", (cutoff_time,)
            )
            conn.commit()
            rows_deleted = cursor.rowcount
            cursor.close()
            return_database_connection(conn)

            logger.info(
                "Cleared old conversations | Deleted: %d messages older than %d hours",
                rows_deleted,
                hours,
            )
            return rows_deleted

        except psycopg2.Error as e:
            logger.error("Database error clearing old conversations: %s", e)
            return 0

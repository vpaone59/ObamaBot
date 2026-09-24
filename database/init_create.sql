-- Users table: Track Discord users with custom nicknames/titles
CREATE TABLE IF NOT EXISTS users (
    discord_id BIGINT PRIMARY KEY,
    display_name TEXT NOT NULL,
    custom_nickname TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Conversations table: Store conversation history for context
CREATE TABLE IF NOT EXISTS conversations (
    id BIGSERIAL PRIMARY KEY,
    discord_id BIGINT NOT NULL REFERENCES users(discord_id) ON DELETE CASCADE,
    role TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Index for faster queries on conversations
CREATE INDEX IF NOT EXISTS idx_conversations_discord_id_created_at 
ON conversations(discord_id, created_at DESC);

-- Index for cleanup queries (finding old conversations)
CREATE INDEX IF NOT EXISTS idx_conversations_created_at 
ON conversations(created_at);

# Supabase Database Schema for AI Study Assistant

This document describes the database schema needed for the Supabase backend integration.

## Overview

The AI Study Assistant uses Supabase (PostgreSQL) to store:
- Learning sessions
- Questions and answers
- Conversation history
- Progress tracking events
- Hints provided
- Analytics data

## Setup Instructions

### 1. Create Supabase Project

1. Go to [https://supabase.com](https://supabase.com)
2. Create a free account (if you don't have one)
3. Create a new project
4. Note down your:
   - **Project URL** (e.g., https://xxxxx.supabase.co)
   - **Anon/Public Key** (from Settings → API)

### 2. Configure Environment Variables

Update your `.env` file:

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key-here
SUPABASE_ENABLED=true
```

### 3. Create Database Tables

Go to your Supabase project → SQL Editor and run the following SQL:

```sql
-- =====================================================
-- SESSIONS TABLE
-- Stores learning session information
-- =====================================================
CREATE TABLE sessions (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id TEXT NOT NULL DEFAULT 'anonymous',
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    ended_at TIMESTAMPTZ,
    status TEXT NOT NULL DEFAULT 'active',
    total_questions INTEGER DEFAULT 0,
    total_hints INTEGER DEFAULT 0,
    session_stats JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Index for faster queries
CREATE INDEX idx_sessions_user_id ON sessions(user_id);
CREATE INDEX idx_sessions_status ON sessions(status);
CREATE INDEX idx_sessions_started_at ON sessions(started_at DESC);

-- =====================================================
-- QUESTIONS TABLE
-- Stores questions asked by students
-- =====================================================
CREATE TABLE questions (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    session_id UUID REFERENCES sessions(id) ON DELETE CASCADE,
    question_text TEXT NOT NULL,
    question_type TEXT NOT NULL,
    strategy_used TEXT NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_questions_session_id ON questions(session_id);
CREATE INDEX idx_questions_type ON questions(question_type);
CREATE INDEX idx_questions_timestamp ON questions(timestamp DESC);

-- =====================================================
-- CONVERSATIONS TABLE
-- Stores full conversation history (user + assistant)
-- =====================================================
CREATE TABLE conversations (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    session_id UUID REFERENCES sessions(id) ON DELETE CASCADE,
    role TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_conversations_session_id ON conversations(session_id);
CREATE INDEX idx_conversations_timestamp ON conversations(timestamp ASC);

-- =====================================================
-- PROGRESS_EVENTS TABLE
-- Tracks learning progress events
-- =====================================================
CREATE TABLE progress_events (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    session_id UUID REFERENCES sessions(id) ON DELETE CASCADE,
    event_type TEXT NOT NULL,
    event_data JSONB NOT NULL DEFAULT '{}',
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_progress_session_id ON progress_events(session_id);
CREATE INDEX idx_progress_event_type ON progress_events(event_type);
CREATE INDEX idx_progress_timestamp ON progress_events(timestamp DESC);

-- =====================================================
-- HINTS TABLE
-- Stores hints provided to students
-- =====================================================
CREATE TABLE hints (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    session_id UUID REFERENCES sessions(id) ON DELETE CASCADE,
    question TEXT NOT NULL,
    hint_number INTEGER NOT NULL CHECK (hint_number BETWEEN 1 AND 3),
    hint_content TEXT NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_hints_session_id ON hints(session_id);
CREATE INDEX idx_hints_timestamp ON hints(timestamp DESC);

-- =====================================================
-- FUNCTIONS & TRIGGERS
-- Automatically update timestamps
-- =====================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for sessions table
CREATE TRIGGER update_sessions_updated_at
    BEFORE UPDATE ON sessions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- ROW LEVEL SECURITY (RLS) POLICIES
-- For future multi-user support
-- =====================================================

-- Enable RLS on all tables
ALTER TABLE sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE questions ENABLE ROW LEVEL SECURITY;
ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE progress_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE hints ENABLE ROW LEVEL SECURITY;

-- Allow anonymous users to insert/select their own data
-- For now, we'll use permissive policies since we're using anonymous access

CREATE POLICY "Allow anonymous access to sessions"
    ON sessions FOR ALL
    TO anon
    USING (true)
    WITH CHECK (true);

CREATE POLICY "Allow anonymous access to questions"
    ON questions FOR ALL
    TO anon
    USING (true)
    WITH CHECK (true);

CREATE POLICY "Allow anonymous access to conversations"
    ON conversations FOR ALL
    TO anon
    USING (true)
    WITH CHECK (true);

CREATE POLICY "Allow anonymous access to progress_events"
    ON progress_events FOR ALL
    TO anon
    USING (true)
    WITH CHECK (true);

CREATE POLICY "Allow anonymous access to hints"
    ON hints FOR ALL
    TO anon
    USING (true)
    WITH CHECK (true);

-- =====================================================
-- VIEWS FOR ANALYTICS
-- =====================================================

-- View for session analytics
CREATE OR REPLACE VIEW session_analytics AS
SELECT 
    s.id,
    s.user_id,
    s.started_at,
    s.ended_at,
    s.status,
    COUNT(DISTINCT q.id) as total_questions,
    COUNT(DISTINCT h.id) as total_hints,
    COUNT(DISTINCT CASE WHEN pe.event_type = 'hint_requested' THEN pe.id END) as hint_requests,
    EXTRACT(EPOCH FROM (COALESCE(s.ended_at, NOW()) - s.started_at))/60 as session_duration_minutes
FROM sessions s
LEFT JOIN questions q ON s.id = q.session_id
LEFT JOIN hints h ON s.id = h.session_id
LEFT JOIN progress_events pe ON s.id = pe.session_id
GROUP BY s.id, s.user_id, s.started_at, s.ended_at, s.status;

-- View for question type distribution
CREATE OR REPLACE VIEW question_type_stats AS
SELECT 
    question_type,
    COUNT(*) as count,
    COUNT(*) * 100.0 / SUM(COUNT(*)) OVER () as percentage
FROM questions
GROUP BY question_type
ORDER BY count DESC;

-- View for strategy usage
CREATE OR REPLACE VIEW strategy_usage_stats AS
SELECT 
    strategy_used,
    COUNT(*) as count,
    COUNT(*) * 100.0 / SUM(COUNT(*)) OVER () as percentage
FROM questions
GROUP BY strategy_used
ORDER BY count DESC;
```

## Verify Setup

After running the SQL, verify the tables were created:

```sql
-- List all tables
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public';

-- Check sessions table structure
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'sessions';
```

## Using the Supabase Integration

### In Your Application

The integration works automatically once configured:

```python
from src.services.study_assistant import StudyAssistant

# Initialize assistant (automatically connects to Supabase if configured)
assistant = StudyAssistant()

# Check Supabase status
status = assistant.check_supabase_status()
print(status)

# Process questions (automatically saved to Supabase)
result = assistant.process_question("What is photosynthesis?")
```

### Querying Data

You can query your data directly from Supabase dashboard or using SQL:

```sql
-- Get recent sessions
SELECT * FROM sessions ORDER BY started_at DESC LIMIT 10;

-- Get questions for a specific session
SELECT * FROM questions 
WHERE session_id = 'your-session-id' 
ORDER BY timestamp;

-- Get conversation history
SELECT role, content, timestamp 
FROM conversations 
WHERE session_id = 'your-session-id' 
ORDER BY timestamp;

-- Analytics: Most common question types
SELECT * FROM question_type_stats;

-- Analytics: Strategy effectiveness
SELECT * FROM strategy_usage_stats;
```

## Data Privacy & Security

### Current Setup (Anonymous Users)
- All data is stored with `user_id = 'anonymous'`
- No personal information is collected
- Sessions are isolated by UUID

### Future: User Authentication
To add user authentication:

1. Enable Supabase Auth in your project
2. Update RLS policies to filter by `auth.uid()`
3. Modify the application to pass user IDs

## Backup & Export

### Export Data as CSV

From Supabase dashboard:
1. Go to Table Editor
2. Select a table
3. Click Export → CSV

### Programmatic Backup

```python
from src.services.supabase_service import SupabaseService

supabase = SupabaseService()

# Get all sessions
sessions = supabase.client.table('sessions').select('*').execute()

# Export to JSON
import json
with open('backup_sessions.json', 'w') as f:
    json.dump(sessions.data, f, indent=2)
```

## Troubleshooting

### Connection Issues

```python
from src.services.supabase_service import SupabaseService

supabase = SupabaseService()
status = supabase.test_connection()
print(status)
```

### Common Errors

**Error: "relation does not exist"**
- Run the SQL schema creation script
- Verify tables exist in Supabase dashboard

**Error: "JWT expired"**
- Your anon key might be wrong
- Check Settings → API in Supabase dashboard

**Error: "permission denied"**
- RLS policies might be blocking access
- Verify policies are created correctly

### Fallback Mode

The application gracefully falls back to local storage if Supabase is unavailable:

```env
# Disable Supabase temporarily
SUPABASE_ENABLED=false
```

Data will be stored in local JSON files instead.

## Performance Optimization

### Indexes
All necessary indexes are created in the schema for optimal query performance.

### Query Limits
```python
# Limit conversation history retrieval
history = supabase.get_conversation_history(session_id, limit=50)
```

### Cleanup Old Data
```sql
-- Delete sessions older than 90 days
DELETE FROM sessions 
WHERE started_at < NOW() - INTERVAL '90 days';
```

## Next Steps

1. ✅ Run the SQL schema script in Supabase
2. ✅ Configure `.env` with your Supabase credentials
3. ✅ Test the connection: `python -c "from src.services.supabase_service import SupabaseService; print(SupabaseService().test_connection())"`
4. ✅ Start using: `python main.py`

## Additional Resources

- [Supabase Documentation](https://supabase.com/docs)
- [Supabase Python Client](https://github.com/supabase-community/supabase-py)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

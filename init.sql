-- AI Notebook System Database Schema
-- This script initializes the database with all required tables for SQLAlchemy models

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table
CREATE TABLE users (
    id VARCHAR PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(255),
    hashed_password VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'viewer' CHECK (role IN ('viewer', 'editor', 'admin')),
    is_active BOOLEAN DEFAULT TRUE,
    user_metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Projects table
CREATE TABLE projects (
    id VARCHAR PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    owner_id VARCHAR NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    is_public BOOLEAN DEFAULT FALSE,
    project_metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Blocks table
CREATE TABLE blocks (
    id VARCHAR PRIMARY KEY,
    project_id VARCHAR NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    owner_id VARCHAR NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    kind VARCHAR(50) NOT NULL CHECK (kind IN ('CODE', 'MARKDOWN', 'SQL', 'TEXT')),
    language VARCHAR(50),
    title VARCHAR(255),
    content TEXT,
    position_x INTEGER DEFAULT 0,
    position_y INTEGER DEFAULT 0,
    status VARCHAR(50) DEFAULT 'IDLE' CHECK (status IN ('IDLE', 'RUNNING', 'COMPLETED', 'FAILED', 'STALE')),
    
    -- Output storage fields
    outputs JSONB DEFAULT '[]',
    last_execution_output TEXT,
    last_execution_error TEXT,
    execution_count INTEGER DEFAULT 0,
    
    block_metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Edges table (DAG dependencies)
CREATE TABLE edges (
    id VARCHAR PRIMARY KEY,
    project_id VARCHAR NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    from_block_id VARCHAR NOT NULL REFERENCES blocks(id) ON DELETE CASCADE,
    to_block_id VARCHAR NOT NULL REFERENCES blocks(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(from_block_id, to_block_id)
);

-- Datasets table
CREATE TABLE datasets (
    id VARCHAR PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    source_type VARCHAR(50) NOT NULL CHECK (source_type IN ('file', 'sql', 's3', 'api')),
    source_path TEXT,
    source_connection JSONB,
    tags TEXT[],
    owner_id VARCHAR NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    last_profiled_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Dataset profiles table
CREATE TABLE dataset_profiles (
    id VARCHAR PRIMARY KEY,
    dataset_id VARCHAR NOT NULL REFERENCES datasets(id) ON DELETE CASCADE,
    schema JSONB NOT NULL,
    row_count_estimate BIGINT,
    preview_data JSONB,
    statistics JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Runs table (execution history)
CREATE TABLE runs (
    id VARCHAR PRIMARY KEY,
    project_id VARCHAR NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    kernel_id VARCHAR(255),
    status VARCHAR(50) DEFAULT 'pending' CHECK (status IN ('pending', 'running', 'completed', 'failed', 'cancelled')),
    started_at TIMESTAMP WITH TIME ZONE,
    finished_at TIMESTAMP WITH TIME ZONE,
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Block runs table (individual block execution)
CREATE TABLE block_runs (
    id VARCHAR PRIMARY KEY,
    run_id VARCHAR NOT NULL REFERENCES runs(id) ON DELETE CASCADE,
    block_id VARCHAR NOT NULL REFERENCES blocks(id) ON DELETE CASCADE,
    status VARCHAR(50) DEFAULT 'pending' CHECK (status IN ('pending', 'running', 'completed', 'failed', 'cancelled')),
    started_at TIMESTAMP WITH TIME ZONE,
    finished_at TIMESTAMP WITH TIME ZONE,
    execution_time_ms INTEGER,
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Artifacts table (outputs, images, etc.)
CREATE TABLE artifacts (
    id VARCHAR PRIMARY KEY,
    block_run_id VARCHAR NOT NULL REFERENCES block_runs(id) ON DELETE CASCADE,
    type VARCHAR(50) NOT NULL CHECK (type IN ('stream', 'display', 'html', 'png', 'table', 'error')),
    mime_type VARCHAR(100),
    storage_path TEXT NOT NULL,
    size_bytes BIGINT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Project versions table (for version control)
CREATE TABLE project_versions (
    id VARCHAR PRIMARY KEY,
    project_id VARCHAR NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    version_number INTEGER NOT NULL,
    snapshot JSONB NOT NULL,
    created_by VARCHAR NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(project_id, version_number)
);

-- Project sharing table (RBAC)
CREATE TABLE project_sharing (
    id VARCHAR PRIMARY KEY,
    project_id VARCHAR NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    user_id VARCHAR NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    permission VARCHAR(50) NOT NULL CHECK (permission IN ('viewer', 'editor', 'admin')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(project_id, user_id)
);

-- AI conversations table (for LLM orchestration)
CREATE TABLE ai_conversations (
    id VARCHAR PRIMARY KEY,
    project_id VARCHAR NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    user_id VARCHAR NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    conversation_data JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX idx_blocks_project_id ON blocks(project_id);
CREATE INDEX idx_blocks_owner_id ON blocks(owner_id);
CREATE INDEX idx_edges_project_id ON edges(project_id);
CREATE INDEX idx_edges_from_block ON edges(from_block_id);
CREATE INDEX idx_edges_to_block ON edges(to_block_id);
CREATE INDEX idx_runs_project_id ON runs(project_id);
CREATE INDEX idx_block_runs_run_id ON block_runs(run_id);
CREATE INDEX idx_block_runs_block_id ON block_runs(block_id);
CREATE INDEX idx_artifacts_block_run_id ON artifacts(block_run_id);
CREATE INDEX idx_datasets_owner_id ON datasets(owner_id);
CREATE INDEX idx_project_sharing_project_id ON project_sharing(project_id);
CREATE INDEX idx_project_sharing_user_id ON project_sharing(user_id);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply updated_at triggers
CREATE TRIGGER update_projects_updated_at BEFORE UPDATE ON projects
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_blocks_updated_at BEFORE UPDATE ON blocks
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_datasets_updated_at BEFORE UPDATE ON datasets
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert default admin user
INSERT INTO users (id, email, username, full_name, hashed_password, role) 
VALUES ('admin_123', 'admin@notebook.ai', 'admin', 'System Administrator', 'hashed_admin_password', 'admin')
ON CONFLICT (email) DO NOTHING;

-- Insert sample project
INSERT INTO projects (id, name, description, owner_id) 
SELECT 'sample_project_123', 'Sample Sales Analysis', 'A sample project for analyzing sales data', id 
FROM users WHERE email = 'admin@notebook.ai'
ON CONFLICT DO NOTHING; 
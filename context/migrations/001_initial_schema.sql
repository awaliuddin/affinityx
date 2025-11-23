-- Initial database schema for AI Product Studio
-- PostgreSQL

-- Projects table
CREATE TABLE IF NOT EXISTS projects (
    project_id VARCHAR(255) PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    goal TEXT NOT NULL,
    constraints JSONB NOT NULL DEFAULT '{}',
    user_preferences JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_project_user_created ON projects(user_id, created_at);

-- Tasks table
CREATE TABLE IF NOT EXISTS tasks (
    task_id VARCHAR(255) PRIMARY KEY,
    project_id VARCHAR(255) NOT NULL REFERENCES projects(project_id) ON DELETE CASCADE,
    agent VARCHAR(50) NOT NULL,
    kind VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    depends_on JSONB NOT NULL DEFAULT '[]',
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_task_project_status ON tasks(project_id, status);

-- Agent history table
CREATE TABLE IF NOT EXISTS agent_history (
    id VARCHAR(255) PRIMARY KEY,
    project_id VARCHAR(255) NOT NULL REFERENCES projects(project_id) ON DELETE CASCADE,
    task_id VARCHAR(255) NOT NULL,
    agent VARCHAR(50) NOT NULL,
    status VARCHAR(50) NOT NULL,
    response_json JSONB NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_history_project_created ON agent_history(project_id, created_at);
CREATE INDEX IF NOT EXISTS idx_history_task ON agent_history(task_id);

-- Deployment info table
CREATE TABLE IF NOT EXISTS deployment_info (
    project_id VARCHAR(255) PRIMARY KEY REFERENCES projects(project_id) ON DELETE CASCADE,
    app_url VARCHAR(500),
    deployment_id VARCHAR(255),
    status VARCHAR(50),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

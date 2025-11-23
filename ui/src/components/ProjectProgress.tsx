import React, { useState, useEffect } from 'react';
import './ProjectProgress.css';

interface Task {
  task_id: string;
  agent: string;
  kind: string;
  description: string;
  status: string;
}

interface ProjectState {
  project_id: string;
  goal: string;
  task_graph: Task[];
  deployment_info: {
    app_url?: string;
    status?: string;
  };
}

interface ProjectProgressProps {
  projectId: string;
  onReset: () => void;
}

export const ProjectProgress: React.FC<ProjectProgressProps> = ({ projectId, onReset }) => {
  const [project, setProject] = useState<ProjectState | null>(null);
  const [loading, setLoading] = useState(true);
  const [executing, setExecuting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchProject();
    const interval = setInterval(fetchProject, 2000);
    return () => clearInterval(interval);
  }, [projectId]);

  const fetchProject = async () => {
    try {
      const response = await fetch(`http://localhost:8000/projects/${projectId}`);
      if (!response.ok) throw new Error('Failed to fetch project');
      const data = await response.json();
      setProject(data.project);
      setLoading(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch project');
      setLoading(false);
    }
  };

  const executeAllTasks = async () => {
    setExecuting(true);
    try {
      const response = await fetch(`http://localhost:8000/projects/${projectId}/execute-all`, {
        method: 'POST',
      });
      if (!response.ok) throw new Error('Failed to execute tasks');
      await fetchProject();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to execute tasks');
    } finally {
      setExecuting(false);
    }
  };

  if (loading) {
    return <div className="loading">Loading project...</div>;
  }

  if (error) {
    return (
      <div className="error">
        <p>Error: {error}</p>
        <button onClick={onReset}>Start Over</button>
      </div>
    );
  }

  if (!project) {
    return null;
  }

  const completedTasks = project.task_graph.filter(t => t.status === 'success').length;
  const totalTasks = project.task_graph.length;
  const progress = (completedTasks / totalTasks) * 100;
  const isComplete = completedTasks === totalTasks;

  return (
    <div className="project-progress">
      <div className="progress-header">
        <h2>Building Your App</h2>
        <p className="goal">{project.goal}</p>

        <div className="progress-bar-container">
          <div className="progress-bar" style={{ width: `${progress}%` }}></div>
        </div>
        <p className="progress-text">
          {completedTasks} of {totalTasks} tasks completed ({Math.round(progress)}%)
        </p>
      </div>

      <div className="actions">
        {!isComplete && !executing && (
          <button onClick={executeAllTasks} className="execute-button">
            ▶️ Execute All Tasks
          </button>
        )}
        {executing && (
          <button className="execute-button" disabled>
            <span className="spinner"></span> Executing...
          </button>
        )}
      </div>

      <div className="task-timeline">
        {project.task_graph.map((task, index) => (
          <div key={task.task_id} className={`task-item task-${task.status}`}>
            <div className="task-number">{index + 1}</div>
            <div className="task-content">
              <div className="task-header">
                <span className="task-agent">{task.agent}</span>
                <span className={`task-status status-${task.status}`}>
                  {task.status === 'success' && '✓'}
                  {task.status === 'pending' && '○'}
                  {task.status === 'in_progress' && '⟳'}
                  {task.status === 'failed' && '✗'}
                  {' '}
                  {task.status}
                </span>
              </div>
              <h3>{task.kind.replace(/_/g, ' ')}</h3>
              <p>{task.description}</p>
            </div>
          </div>
        ))}
      </div>

      {isComplete && project.deployment_info?.app_url && (
        <div className="deployment-success">
          <h2>🎉 Your App is Live!</h2>
          <p>Your micro SaaS has been successfully built and deployed.</p>
          <div className="app-url-card">
            <label>App URL:</label>
            <a href={project.deployment_info.app_url} target="_blank" rel="noopener noreferrer">
              {project.deployment_info.app_url}
            </a>
          </div>
          <button onClick={onReset} className="new-project-button">
            Create Another App
          </button>
        </div>
      )}
    </div>
  );
};

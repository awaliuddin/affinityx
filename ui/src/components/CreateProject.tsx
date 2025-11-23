import React, { useState } from 'react';
import './CreateProject.css';

interface CreateProjectProps {
  onProjectCreated: (projectId: string) => void;
}

export const CreateProject: React.FC<CreateProjectProps> = ({ onProjectCreated }) => {
  const [idea, setIdea] = useState('');
  const [authRequired, setAuthRequired] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!idea.trim()) {
      setError('Please describe your micro SaaS idea');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await fetch('http://localhost:8000/projects', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: 'user_' + Date.now(),
          goal: idea,
          constraints: {
            auth_required: authRequired,
            preferred_stack: 'react',
          },
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to create project');
      }

      const data = await response.json();
      onProjectCreated(data.project_id);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create project');
    } finally {
      setLoading(false);
    }
  };

  const exampleIdeas = [
    'Build a simple todo list app with user authentication',
    'Create a blog platform where users can write and publish articles',
    'Build a dashboard to track personal habits and goals',
    'Create an e-commerce store for handmade products',
  ];

  return (
    <div className="create-project">
      <div className="create-project-card">
        <h2>What would you like to build?</h2>
        <p className="subtitle">
          Describe your micro SaaS idea and let our AI team bring it to life
        </p>

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="idea">Your Idea</label>
            <textarea
              id="idea"
              value={idea}
              onChange={(e) => setIdea(e.target.value)}
              placeholder="Example: Build a simple todo list app with user authentication"
              rows={4}
              disabled={loading}
            />
          </div>

          <div className="form-group checkbox-group">
            <label>
              <input
                type="checkbox"
                checked={authRequired}
                onChange={(e) => setAuthRequired(e.target.checked)}
                disabled={loading}
              />
              <span>Require user authentication</span>
            </label>
          </div>

          {error && (
            <div className="error-message">
              {error}
            </div>
          )}

          <button type="submit" className="submit-button" disabled={loading}>
            {loading ? (
              <>
                <span className="spinner"></span>
                Creating your project...
              </>
            ) : (
              '🚀 Create with AI Team'
            )}
          </button>
        </form>

        <div className="examples">
          <h3>Need inspiration?</h3>
          <ul>
            {exampleIdeas.map((example, index) => (
              <li key={index} onClick={() => setIdea(example)}>
                {example}
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
};

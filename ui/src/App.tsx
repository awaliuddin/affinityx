import React, { useState } from 'react';
import { CreateProject } from './components/CreateProject';
import { ProjectProgress } from './components/ProjectProgress';
import './App.css';

function App() {
  const [projectId, setProjectId] = useState<string | null>(null);

  const handleProjectCreated = (id: string) => {
    setProjectId(id);
  };

  const handleReset = () => {
    setProjectId(null);
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>🤖 AI Product Studio</h1>
        <p className="tagline">Transform ideas into live Micro SaaS applications</p>
      </header>

      <main className="app-main">
        {!projectId ? (
          <CreateProject onProjectCreated={handleProjectCreated} />
        ) : (
          <ProjectProgress projectId={projectId} onReset={handleReset} />
        )}
      </main>

      <footer className="app-footer">
        <p>Powered by multi-agent orchestration • Phase 1 MVP</p>
      </footer>
    </div>
  );
}

export default App;

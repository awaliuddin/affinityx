import React, { useEffect, useState } from 'react';
import './WorkflowVisualization.css';

interface Agent {
  name: string;
  status: 'idle' | 'active' | 'complete' | 'error';
  currentTask?: string;
  progress?: string;
}

interface WorkflowVisualizationProps {
  projectId: string;
}

export const WorkflowVisualization: React.FC<WorkflowVisualizationProps> = ({ projectId }) => {
  const [agents, setAgents] = useState<Agent[]>([
    { name: 'orchestrator', status: 'idle' },
    { name: 'architect', status: 'idle' },
    { name: 'implementer', status: 'idle' },
    { name: 'reviewer', status: 'idle' },
    { name: 'ops', status: 'idle' },
    { name: 'ux_muse', status: 'idle' },
  ]);
  const [messages, setMessages] = useState<string[]>([]);

  useEffect(() => {
    // Connect to WebSocket for real-time updates
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const ws = new WebSocket(`${protocol}//localhost:8000/ws/${projectId}`);

    ws.onopen = () => {
      console.log('WebSocket connected');
      addMessage('🔌 Connected to agent workflow');
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      handleWebSocketMessage(data);
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      addMessage('❌ Connection error');
    };

    ws.onclose = () => {
      console.log('WebSocket disconnected');
      addMessage('🔌 Disconnected from workflow');
    };

    return () => {
      ws.close();
    };
  }, [projectId]);

  const handleWebSocketMessage = (data: any) => {
    switch (data.type) {
      case 'initial_state':
        addMessage('📊 Loaded initial project state');
        break;

      case 'agent_start':
        updateAgentStatus(data.agent, 'active', data.task_kind);
        addMessage(`🚀 ${data.agent} started: ${data.task_kind}`);
        break;

      case 'agent_progress':
        addMessage(`⏳ ${data.message}`);
        break;

      case 'agent_complete':
        updateAgentStatus(data.agent, data.status === 'success' ? 'complete' : 'error');
        const icon = data.status === 'success' ? '✅' : '❌';
        addMessage(`${icon} ${data.agent} ${data.status}`);
        break;

      case 'task_update':
        addMessage(`📝 Task ${data.task_id} → ${data.status}`);
        break;

      case 'project_update':
        // Update overall project state
        break;

      default:
        console.log('Unknown message type:', data.type);
    }
  };

  const updateAgentStatus = (agentName: string, status: Agent['status'], task?: string) => {
    setAgents((prev) =>
      prev.map((agent) =>
        agent.name === agentName
          ? { ...agent, status, currentTask: task }
          : agent
      )
    );
  };

  const addMessage = (message: string) => {
    setMessages((prev) => [...prev.slice(-9), message]); // Keep last 10 messages
  };

  const getAgentIcon = (agentName: string) => {
    const icons: Record<string, string> = {
      orchestrator: '🎭',
      architect: '🏛️',
      implementer: '⚙️',
      reviewer: '🔍',
      ops: '🚢',
      ux_muse: '✨',
    };
    return icons[agentName] || '🤖';
  };

  const getStatusColor = (status: Agent['status']) => {
    const colors: Record<Agent['status'], string> = {
      idle: '#9ca3af',
      active: '#3b82f6',
      complete: '#10b981',
      error: '#ef4444',
    };
    return colors[status];
  };

  return (
    <div className="workflow-visualization">
      <h3>🔄 Agent Workflow</h3>

      <div className="agents-grid">
        {agents.map((agent) => (
          <div
            key={agent.name}
            className={`agent-card agent-${agent.status}`}
            style={{ borderColor: getStatusColor(agent.status) }}
          >
            <div className="agent-icon">{getAgentIcon(agent.name)}</div>
            <div className="agent-info">
              <h4>{agent.name}</h4>
              <span className="agent-status" style={{ color: getStatusColor(agent.status) }}>
                {agent.status}
              </span>
              {agent.currentTask && (
                <p className="agent-task">{agent.currentTask.replace(/_/g, ' ')}</p>
              )}
            </div>
            {agent.status === 'active' && (
              <div className="agent-pulse"></div>
            )}
          </div>
        ))}
      </div>

      <div className="workflow-messages">
        <h4>📡 Live Activity</h4>
        <div className="messages-list">
          {messages.length === 0 ? (
            <p className="no-messages">Waiting for agent activity...</p>
          ) : (
            messages.map((msg, index) => (
              <div key={index} className="message-item">
                {msg}
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};

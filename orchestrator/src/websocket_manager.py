"""
WebSocket manager for real-time agent execution updates.
"""
from typing import Dict, Set
from fastapi import WebSocket
import json
import asyncio


class ConnectionManager:
    """Manages WebSocket connections for real-time updates"""

    def __init__(self):
        # Map of project_id -> set of WebSocket connections
        self.active_connections: Dict[str, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, project_id: str):
        """Accept and register a new WebSocket connection"""
        await websocket.accept()
        if project_id not in self.active_connections:
            self.active_connections[project_id] = set()
        self.active_connections[project_id].add(websocket)

    def disconnect(self, websocket: WebSocket, project_id: str):
        """Remove a WebSocket connection"""
        if project_id in self.active_connections:
            self.active_connections[project_id].discard(websocket)
            if not self.active_connections[project_id]:
                del self.active_connections[project_id]

    async def send_message(self, project_id: str, message: dict):
        """Send a message to all connections for a project"""
        if project_id not in self.active_connections:
            return

        # Create list to avoid modification during iteration
        connections = list(self.active_connections[project_id])

        for connection in connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                print(f"Error sending message to WebSocket: {e}")
                self.disconnect(connection, project_id)

    async def broadcast_agent_start(self, project_id: str, task_id: str, agent: str, task_kind: str):
        """Broadcast that an agent has started execution"""
        await self.send_message(
            project_id,
            {
                "type": "agent_start",
                "task_id": task_id,
                "agent": agent,
                "task_kind": task_kind,
                "timestamp": asyncio.get_event_loop().time(),
            },
        )

    async def broadcast_agent_progress(self, project_id: str, task_id: str, message: str):
        """Broadcast agent progress update"""
        await self.send_message(
            project_id,
            {
                "type": "agent_progress",
                "task_id": task_id,
                "message": message,
                "timestamp": asyncio.get_event_loop().time(),
            },
        )

    async def broadcast_agent_complete(
        self, project_id: str, task_id: str, agent: str, status: str, result: dict
    ):
        """Broadcast that an agent has completed execution"""
        await self.send_message(
            project_id,
            {
                "type": "agent_complete",
                "task_id": task_id,
                "agent": agent,
                "status": status,
                "result": result,
                "timestamp": asyncio.get_event_loop().time(),
            },
        )

    async def broadcast_task_update(self, project_id: str, task_id: str, status: str):
        """Broadcast task status update"""
        await self.send_message(
            project_id,
            {
                "type": "task_update",
                "task_id": task_id,
                "status": status,
                "timestamp": asyncio.get_event_loop().time(),
            },
        )

    async def broadcast_project_update(self, project_id: str, project_data: dict):
        """Broadcast complete project state update"""
        await self.send_message(
            project_id,
            {
                "type": "project_update",
                "project": project_data,
                "timestamp": asyncio.get_event_loop().time(),
            },
        )


# Global connection manager
manager = ConnectionManager()

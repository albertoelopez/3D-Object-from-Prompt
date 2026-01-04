from fastapi import WebSocket
from typing import Dict, Set, Any
import json
import asyncio


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket, job_id: str):
        await websocket.accept()
        async with self._lock:
            if job_id not in self.active_connections:
                self.active_connections[job_id] = set()
            self.active_connections[job_id].add(websocket)

    async def disconnect(self, websocket: WebSocket, job_id: str):
        async with self._lock:
            if job_id in self.active_connections:
                self.active_connections[job_id].discard(websocket)
                if not self.active_connections[job_id]:
                    del self.active_connections[job_id]

    async def send_message(self, websocket: WebSocket, message: Dict[str, Any]):
        try:
            await websocket.send_json(message)
        except Exception:
            pass

    async def broadcast_to_job(self, job_id: str, message: Dict[str, Any]):
        async with self._lock:
            connections = self.active_connections.get(job_id, set()).copy()

        disconnected = set()
        for connection in connections:
            try:
                await connection.send_json(message)
            except Exception:
                disconnected.add(connection)

        if disconnected:
            async with self._lock:
                if job_id in self.active_connections:
                    self.active_connections[job_id] -= disconnected

    def get_connection_count(self, job_id: str) -> int:
        return len(self.active_connections.get(job_id, set()))


manager = ConnectionManager()


async def broadcast_to_job(job_id: str, message: Dict[str, Any]):
    await manager.broadcast_to_job(job_id, message)

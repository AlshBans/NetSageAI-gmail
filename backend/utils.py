# backend/utils.py
import asyncio
from typing import List, Dict, Any
from fastapi import WebSocket

class WSManager:
    def __init__(self):
        self._connections: List[WebSocket] = []

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self._connections.append(ws)

    async def disconnect(self, ws: WebSocket):
        try:
            self._connections.remove(ws)
        except ValueError:
            pass

    async def broadcast(self, message: Dict[str, Any]):
        dead = []
        for ws in list(self._connections):
            try:
                await ws.send_json(message)
            except Exception:
                dead.append(ws)
        for d in dead:
            await self.disconnect(d)

wsmanager = WSManager()

def email_to_dict(e):
    return {
        'id': e.id,
        'uid': e.uid,
        'timestamp': e.ts.isoformat() if hasattr(e.ts,'isoformat') else str(e.ts),
        'sender': e.sender,
        'recipients': e.recipients,
        'subject': e.subject,
        'size': e.size,
        'attachments': bool(e.has_attachment),
        'anomaly_score': float(e.anomaly_score or 0.0),
    }

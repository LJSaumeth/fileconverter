from __future__ import annotations

from contextlib import suppress
from typing import TYPE_CHECKING

from fastapi import WebSocket

from domain.entities import ConversionProgress

if TYPE_CHECKING:
    from adapters.input.websocket.progress_websocket import WebSocketNotifierAdapter


class ConnectionManager:
    """Manages active WebSocket connections keyed by client ID.

    Each client that wants real-time progress opens a WebSocket to
    ``/ws/{client_id}`` and is registered here. When a conversion
    job reports progress, the notifier looks up the client's WebSocket
    by the ``client_id`` stored in the job options and pushes the
    update.
    """

    def __init__(self) -> None:
        self._connections: dict[str, WebSocket] = {}

    async def connect(self, client_id: str, websocket: WebSocket) -> None:
        await websocket.accept()
        self._connections[client_id] = websocket

    def disconnect(self, client_id: str) -> None:
        self._connections.pop(client_id, None)

    def get_notifier(self, client_id: str) -> WebSocketNotifierAdapter | None:
        ws = self._connections.get(client_id)
        if ws is None:
            return None
        from adapters.input.websocket.progress_websocket import WebSocketNotifierAdapter

        return WebSocketNotifierAdapter(ws)

    async def broadcast(self, progress: ConversionProgress) -> None:
        """Send progress to ALL connected clients (admin use)."""
        for websocket in list(self._connections.values()):
            with suppress(Exception):
                await websocket.send_json(
                    {
                        "job_id": str(progress.job_id),
                        "percentage": progress.percentage,
                        "status": progress.status.value,
                        "message": progress.message,
                    }
                )

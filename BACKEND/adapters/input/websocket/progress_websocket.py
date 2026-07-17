from contextlib import suppress

from fastapi import WebSocket

from domain.entities import ConversionProgress
from domain.ports.output.progress_notifier_port import ProgressNotifierPort


class WebSocketNotifierAdapter(ProgressNotifierPort):
    """Sends conversion progress to a single WebSocket client.

    This adapter is created per-client by ``ConnectionManager`` and
    injected into the convert use case when the client has an active
    WebSocket connection.
    """

    def __init__(self, websocket: WebSocket) -> None:
        self._websocket = websocket

    async def notify(self, progress: ConversionProgress) -> None:
        with suppress(Exception):
            await self._websocket.send_json(
                {
                    "job_id": str(progress.job_id),
                    "percentage": progress.percentage,
                    "status": progress.status.value,
                    "message": progress.message,
                }
            )

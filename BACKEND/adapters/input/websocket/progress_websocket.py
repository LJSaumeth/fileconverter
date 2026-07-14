
from fastapi import WebSocket

from domain.entities import ConversionProgress
from domain.ports.output.progress_notifier_port import ProgressNotifierPort


class WebSocketNotifierAdapter(ProgressNotifierPort):
    def __init__(self, websocket: WebSocket):
        self._websocket = websocket

    async def notify(self, progress: ConversionProgress) -> None:
        from contextlib import suppress

        with suppress(Exception):
            await self._websocket.send_json(
                {
                    "job_id": str(progress.job_id),
                    "percentage": progress.percentage,
                    "status": progress.status.value,
                    "message": progress.message,
                }
            )

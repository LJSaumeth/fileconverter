from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from fastapi import WebSocket

from adapters.input.websocket.connection_manager import ConnectionManager
from adapters.input.websocket.progress_websocket import WebSocketNotifierAdapter
from domain.entities import ConversionProgress, ConversionStatus


@pytest.fixture
def mock_websocket():
    ws = MagicMock(spec=WebSocket)
    ws.send_json = AsyncMock()
    ws.accept = AsyncMock()
    ws.receive_text = AsyncMock()
    return ws


class TestWebSocketNotifierAdapter:
    """Tests for the per-client progress notifier."""

    async def test_notify_sends_json(self, mock_websocket):
        adapter = WebSocketNotifierAdapter(mock_websocket)
        progress = ConversionProgress(
            job_id=uuid4(),
            percentage=50,
            status=ConversionStatus.IN_PROGRESS,
            message="Processing page 5 of 10",
        )

        await adapter.notify(progress)

        mock_websocket.send_json.assert_awaited_once()
        call_kwargs = mock_websocket.send_json.call_args[0][0]
        assert call_kwargs["percentage"] == 50
        assert call_kwargs["status"] == "in_progress"
        assert call_kwargs["message"] == "Processing page 5 of 10"

    async def test_notify_suppresses_send_failure(self, mock_websocket):
        mock_websocket.send_json.side_effect = RuntimeError("connection lost")
        adapter = WebSocketNotifierAdapter(mock_websocket)
        progress = ConversionProgress(
            job_id=uuid4(),
            percentage=100,
            status=ConversionStatus.COMPLETED,
        )

        # Must not raise despite send failure
        await adapter.notify(progress)


class TestConnectionManager:
    """Tests for WebSocket connection registry."""

    async def test_connect_and_disconnect(self, mock_websocket):
        manager = ConnectionManager()
        await manager.connect("client-1", mock_websocket)

        notifier = manager.get_notifier("client-1")
        assert notifier is not None

        manager.disconnect("client-1")
        assert manager.get_notifier("client-1") is None

    async def test_get_notifier_returns_none_for_unknown(self):
        manager = ConnectionManager()
        assert manager.get_notifier("unknown") is None

    async def test_broadcast_sends_to_all(self, mock_websocket):
        ws2 = MagicMock(spec=WebSocket)
        ws2.send_json = AsyncMock()

        manager = ConnectionManager()
        await manager.connect("c1", mock_websocket)
        await manager.connect("c2", ws2)

        progress = ConversionProgress(
            job_id=uuid4(),
            percentage=100,
            status=ConversionStatus.COMPLETED,
        )
        await manager.broadcast(progress)

        assert mock_websocket.send_json.await_count == 1
        assert ws2.send_json.await_count == 1

    async def test_disconnect_removes_only_target(self, mock_websocket):
        ws2 = MagicMock(spec=WebSocket)
        ws2.send_json = AsyncMock()

        manager = ConnectionManager()
        await manager.connect("c1", mock_websocket)
        await manager.connect("c2", ws2)

        manager.disconnect("c1")

        assert manager.get_notifier("c1") is None
        assert manager.get_notifier("c2") is not None

    async def test_broadcast_skips_failed_connections(self, mock_websocket):
        ws2 = MagicMock(spec=WebSocket)
        ws2.send_json = AsyncMock(side_effect=RuntimeError("gone"))

        manager = ConnectionManager()
        await manager.connect("c1", mock_websocket)
        await manager.connect("c2", ws2)

        progress = ConversionProgress(
            job_id=uuid4(),
            percentage=100,
            status=ConversionStatus.COMPLETED,
        )
        # Must not raise despite ws2 failure
        await manager.broadcast(progress)

        assert mock_websocket.send_json.await_count == 1

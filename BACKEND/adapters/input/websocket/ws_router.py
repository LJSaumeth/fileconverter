from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from adapters.input.websocket.connection_manager import ConnectionManager

router = APIRouter(prefix="/ws", tags=["websocket"])


@router.websocket("/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str) -> None:
    manager: ConnectionManager = websocket.app.state.ws_manager
    await manager.connect(client_id, websocket)
    try:
        while True:
            # Keep connection alive; client may send pings or we may
            # receive disconnect on read.
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(client_id)
    except Exception:
        manager.disconnect(client_id)

from fastapi import WebSocket, WebSocketDisconnect
from datetime import datetime
import json

from app.api.websocket.manager import manager
from app.core.queue import JobQueue
from app.core.redis import get_redis


async def websocket_endpoint(websocket: WebSocket, job_id: str):
    await manager.connect(websocket, job_id)

    try:
        queue = JobQueue(get_redis())
        job = await queue.get_job(job_id)

        if job:
            await manager.send_message(websocket, {
                "type": "connected",
                "job_id": job_id,
                "current_status": job["status"],
                "progress": job.get("progress", 0),
                "timestamp": datetime.utcnow().isoformat()
            })
        else:
            await manager.send_message(websocket, {
                "type": "error",
                "job_id": job_id,
                "error": {"code": "JOB_NOT_FOUND", "message": "Job not found"},
                "timestamp": datetime.utcnow().isoformat()
            })

        while True:
            try:
                data = await websocket.receive_text()
                message = json.loads(data)

                if message.get("type") == "ping":
                    await manager.send_message(websocket, {
                        "type": "pong",
                        "timestamp": datetime.utcnow().isoformat()
                    })
                elif message.get("type") == "subscribe":
                    pass
                elif message.get("type") == "get_status":
                    job = await queue.get_job(job_id)
                    if job:
                        await manager.send_message(websocket, {
                            "type": "status_update",
                            "job_id": job_id,
                            "status": job["status"],
                            "progress": job.get("progress", 0),
                            "stage": job.get("stage"),
                            "stage_progress": job.get("stage_progress", 0),
                            "timestamp": datetime.utcnow().isoformat()
                        })

            except json.JSONDecodeError:
                await manager.send_message(websocket, {
                    "type": "error",
                    "error": {"code": "INVALID_JSON", "message": "Invalid JSON message"},
                    "timestamp": datetime.utcnow().isoformat()
                })

    except WebSocketDisconnect:
        pass
    finally:
        await manager.disconnect(websocket, job_id)

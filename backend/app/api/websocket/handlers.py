from fastapi import WebSocket, WebSocketDisconnect
from datetime import datetime
import json
import asyncio

from app.api.websocket.manager import manager
from app.core.queue import JobQueue
from app.core.redis import get_redis


async def websocket_endpoint(websocket: WebSocket, job_id: str):
    await manager.connect(websocket, job_id)
    last_progress = -1
    last_status = None

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
            last_progress = job.get("progress", 0)
            last_status = job["status"]
        else:
            await manager.send_message(websocket, {
                "type": "error",
                "job_id": job_id,
                "error": {"code": "JOB_NOT_FOUND", "message": "Job not found"},
                "timestamp": datetime.utcnow().isoformat()
            })
            return

        async def poll_job_status():
            nonlocal last_progress, last_status
            while True:
                try:
                    job = await queue.get_job(job_id)
                    if not job:
                        break

                    current_progress = job.get("progress", 0)
                    current_status = job["status"]

                    if current_progress != last_progress or current_status != last_status:
                        last_progress = current_progress
                        last_status = current_status

                        if current_status == "completed":
                            await manager.send_message(websocket, {
                                "type": "completion",
                                "job_id": job_id,
                                "result": job.get("result"),
                                "timestamp": datetime.utcnow().isoformat()
                            })
                            return
                        elif current_status == "failed":
                            await manager.send_message(websocket, {
                                "type": "error",
                                "job_id": job_id,
                                "error": job.get("error", {"code": "UNKNOWN", "message": "Job failed"}),
                                "timestamp": datetime.utcnow().isoformat()
                            })
                            return
                        else:
                            await manager.send_message(websocket, {
                                "type": "progress_update",
                                "job_id": job_id,
                                "status": current_status,
                                "progress": current_progress,
                                "stage": job.get("stage"),
                                "stage_progress": job.get("stage_progress", 0),
                                "timestamp": datetime.utcnow().isoformat()
                            })

                    await asyncio.sleep(0.5)
                except Exception as e:
                    print(f"Polling error: {e}")
                    break

        async def handle_messages():
            while True:
                try:
                    data = await websocket.receive_text()
                    message = json.loads(data)

                    if message.get("type") == "ping":
                        await manager.send_message(websocket, {
                            "type": "pong",
                            "timestamp": datetime.utcnow().isoformat()
                        })

                except json.JSONDecodeError:
                    await manager.send_message(websocket, {
                        "type": "error",
                        "error": {"code": "INVALID_JSON", "message": "Invalid JSON message"},
                        "timestamp": datetime.utcnow().isoformat()
                    })
                except WebSocketDisconnect:
                    break
                except Exception:
                    break

        poll_task = asyncio.create_task(poll_job_status())
        message_task = asyncio.create_task(handle_messages())

        done, pending = await asyncio.wait(
            [poll_task, message_task],
            return_when=asyncio.FIRST_COMPLETED
        )

        for task in pending:
            task.cancel()

    except WebSocketDisconnect:
        pass
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        await manager.disconnect(websocket, job_id)

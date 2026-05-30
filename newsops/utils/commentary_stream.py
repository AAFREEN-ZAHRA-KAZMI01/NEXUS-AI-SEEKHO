import asyncio
from datetime import datetime, timezone
import json
import logging

logger = logging.getLogger(__name__)

# Global dictionary to maintain active WebSocket queues by session_id
active_streams: dict[str, asyncio.Queue] = {}

def create_stream(session_id: str) -> asyncio.Queue:
    """Creates and returns a new asyncio Queue for the given session_id."""
    queue = asyncio.Queue()
    active_streams[session_id] = queue
    return queue

def push_commentary(session_id: str, agent: str, message: str, stage: str):
    """
    Pushes a commentary message to the queue for the given session_id.
    Stage should be "start" | "progress" | "complete".
    """
    if session_id in active_streams:
        queue = active_streams[session_id]
        timestamp = datetime.now(timezone.utc).isoformat()
        
        msg_obj = {
            "session_id": session_id,
            "agent": agent,
            "stage": stage,
            "message": message,
            "timestamp": timestamp
        }
        
        try:
            queue.put_nowait(msg_obj)
        except asyncio.QueueFull:
            logger.warning(f"Queue full for session {session_id}, dropping message: {message}")
    else:
        # If no stream is active, we just drop the commentary
        pass

def close_stream(session_id: str):
    """
    Closes the stream by sending a special 'close' marker and removing it from the dictionary.
    """
    if session_id in active_streams:
        queue = active_streams.pop(session_id)
        try:
            # Send a closing message so the websocket loop knows to exit
            queue.put_nowait({"session_id": session_id, "close": True})
        except Exception:
            pass

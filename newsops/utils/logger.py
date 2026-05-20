import json
from datetime import datetime, timezone


class SessionLogger:
    def __init__(self, session_id: str):
        self.session_id = session_id

    def log(self, agent: str, event: str, data: dict = None):
        entry = {
            "session_id": self.session_id,
            "agent": agent,
            "event": event,
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "data": data or {},
        }
        print(json.dumps(entry))


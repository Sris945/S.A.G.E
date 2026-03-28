"""Session debug NDJSON sink (Cursor debug mode). Remove when investigation ends."""

from __future__ import annotations

import json
import time

LOG_PATH = "/home/s/Documents/SAGE/.cursor/debug-9ef3ee.log"
SESSION_ID = "9ef3ee"


def agent_debug_log(
    location: str,
    message: str,
    *,
    data: dict | None = None,
    hypothesis_id: str = "",
) -> None:
    try:
        payload = {
            "sessionId": SESSION_ID,
            "timestamp": int(time.time() * 1000),
            "location": location,
            "message": message,
            "data": data or {},
            "hypothesisId": hypothesis_id,
        }
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(payload, ensure_ascii=False) + "\n")
    except OSError:
        pass

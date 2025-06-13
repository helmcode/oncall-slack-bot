import json
from datetime import datetime
from typing import List, Dict, Any
import redis

from config.env_vars import config

class RedisStorage:
    """High-level API over Redis for oncall data."""

    def __init__(self):
        self.client: redis.Redis = redis.from_url(config.REDIS_URL, decode_responses=True)

    # --------------------------------------------------
    # Current on-call
    # --------------------------------------------------
    def get_oncall(self, region: str) -> str | None:
        return self.client.get(f"oncall:{region}")

    def set_oncall(self, region: str, slack_id: str):
        self.client.set(f"oncall:{region}", slack_id)

    # --------------------------------------------------
    # Rotation index
    # --------------------------------------------------
    def get_rotation_idx(self, region: str) -> int:
        idx = self.client.get(f"rotation_idx:{region}")
        return int(idx) if idx is not None else -1

    def set_rotation_idx(self, region: str, idx: int):
        self.client.set(f"rotation_idx:{region}", idx)

    # --------------------------------------------------
    # Rotation history
    # --------------------------------------------------
    def push_history(self, region: str, member_id: str):
        entry = {
            "member_id": member_id,
            "timestamp": datetime.now().isoformat(),
        }
        self.client.lpush(f"rotation_history:{region}", json.dumps(entry))
        # keep last 10
        self.client.ltrim(f"rotation_history:{region}", 0, 9)

    def get_latest_history(self, region: str) -> Dict[str, Any] | None:
        raw = self.client.lrange(f"rotation_history:{region}", 0, 0)
        if raw:
            return json.loads(raw[0])
        return None

    def lrange(self, key: str, start: int, end: int) -> List[str]:
        return self.client.lrange(key, start, end)

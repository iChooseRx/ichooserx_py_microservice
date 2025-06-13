from datetime import datetime, timezone

def current_timestamp():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H-%M-%S UTC")
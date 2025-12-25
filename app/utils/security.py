import re

def validate_user_id(user_id: str) -> bool:
    if not user_id or len(user_id) > 255:
        return False
    return bool(re.match(r'^[a-zA-Z0-9_.-]+$', user_id))

def validate_channel_name(channel: str) -> bool:
    if not channel or len(channel) > 64:
        return False
    return bool(re.match(r'^[a-zA-Z0-9_-]+$', channel))
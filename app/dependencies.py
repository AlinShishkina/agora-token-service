from fastapi import Header, HTTPException, Depends
from typing import Optional, Callable
import time
import os
import redis
from redis.exceptions import ConnectionError



REDIS_URL = os.getenv("REDIS_STORAGE_URL", "redis://redis:6380/0")
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "Wb_Sync2024!")
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6380"))
REDIS_DB = int(os.getenv("REDIS_DB", "0"))
REDIS_TIMEOUT = int(os.getenv("REDIS_TIMEOUT", "5"))
REDIS_ENABLED = os.getenv("REDIS_ENABLED", "true").lower() == "true"

redis_client = None
if REDIS_ENABLED:
    try:
        redis_client = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            password=REDIS_PASSWORD,
            db=REDIS_DB,
            socket_timeout=REDIS_TIMEOUT,
            decode_responses=True,
            socket_connect_timeout=REDIS_TIMEOUT
        )
        
        redis_client.ping()
        print("Redis connected successfully")
    except (ConnectionError, Exception) as e:
        print(f"Redis connection failed: {e}. Rate limiting will be disabled.")
        redis_client = None


def get_user_id(x_user_id: Optional[str] = Header(None, alias="X-User-Id")):  
    if not x_user_id:
        raise HTTPException(
            status_code=401,
            detail="X-User-Id header is required"
        )
    return x_user_id


def rate_limit():
  
    RATE_LIMIT_ENABLED = os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true"
    RATE_LIMIT_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", "50"))
    RATE_LIMIT_PERIOD = int(os.getenv("RATE_LIMIT_PERIOD", "60"))
    
    def limiter(user_id: str = Depends(get_user_id)):
        if not RATE_LIMIT_ENABLED or not redis_client:
            return user_id
        
        key = f"rate_limit:{user_id}"
        current_time = time.time()
        window_start = current_time - RATE_LIMIT_PERIOD
        
        try:
            data = redis_client.hgetall(key)
            
            timestamps = [float(ts) for ts in data.get('timestamps', '').split(',') if ts]
            timestamps = [ts for ts in timestamps if ts > window_start]
            
            if len(timestamps) >= RATE_LIMIT_REQUESTS:
                raise HTTPException(
                    status_code=429,
                    detail=f"Rate limit exceeded. {RATE_LIMIT_REQUESTS} requests per {RATE_LIMIT_PERIOD}s"
                )
            
            timestamps.append(current_time)
            redis_client.hset(key, mapping={
                'timestamps': ','.join(map(str, timestamps)),
                'count': len(timestamps)
            })
            redis_client.expire(key, RATE_LIMIT_PERIOD)
            
        except Exception:
            pass
        
        return user_id
    
    return limiter


def rare_limit(window: int = 3600, limit: int = 5) -> Callable:
   
    def limiter(user_id: str = Depends(get_user_id)):
        if not redis_client:
            return user_id  
        
        key = f"rare_limit:{user_id}:{window}:{limit}"
        current_time = time.time()
        
        try:
            data = redis_client.hgetall(key)

            timestamps = [float(ts) for ts in data.get('timestamps', '').split(',') if ts]
            timestamps = [ts for ts in timestamps if current_time - ts < window]
            
            if len(timestamps) >= limit:
                raise HTTPException(
                    status_code=429,
                    detail=f"Слишком много запросов. Лимит: {limit} в {window}с"
                )

            timestamps.append(current_time)
            redis_client.hset(key, mapping={
                'timestamps': ','.join(map(str, timestamps)),
                'count': len(timestamps),
                'window_start': current_time - window
            })
            redis_client.expire(key, window)
            
        except Exception:
            pass
        
        return user_id
    
    return limiter
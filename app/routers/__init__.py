
try:
    from .auth import router as auth_router
    from .tokens import router as tokens_router
    from .rooms import router as rooms_router
    from .health import router as health_router
    
    auth = auth_router
    tokens = tokens_router
    rooms = rooms_router
    health = health_router
    
except ImportError as e:
    print(f"Error importing routers: {e}")
    
    # заглушки
    from fastapi import APIRouter
    
    auth = APIRouter()
    tokens = APIRouter()
    rooms = APIRouter()
    health = APIRouter()
    
    @auth.get("/placeholder")
    def auth_placeholder():
        return {"error": "Auth router not loaded"}
    
    @tokens.get("/placeholder")
    def tokens_placeholder():
        return {"error": "Tokens router not loaded"}
    
    @rooms.get("/placeholder")
    def rooms_placeholder():
        return {"error": "Rooms router not loaded"}
    
    @health.get("/placeholder")
    def health_placeholder():
        return {"error": "Health router not loaded"}
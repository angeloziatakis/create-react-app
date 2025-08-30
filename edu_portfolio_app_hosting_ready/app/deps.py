from fastapi import Request, HTTPException, status
from functools import wraps

def require_login(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        request: Request = kwargs.get("request") or args[0]
        user = request.session.get("user")
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Login required")
        return await func(*args, **kwargs)
    return wrapper

def require_role(role: str):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            request: Request = kwargs.get("request") or args[0]
            user = request.session.get("user")
            if not user or user.get("role") != role:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
            return await func(*args, **kwargs)
        return wrapper
    return decorator

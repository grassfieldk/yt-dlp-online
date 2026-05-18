from fastapi import Header, HTTPException, status

from .config import settings


def verify_api_key(x_api_key: str = Header(..., description="API key for authentication")) -> None:
    """FastAPI dependency that validates the X-Api-Key request header."""
    if x_api_key != settings.api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )

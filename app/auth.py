import os
from fastapi import Header, HTTPException, status


def verify_api_key(x_api_key: str = Header(..., alias="X-API-Key")) -> None:
    valid_key = os.getenv("API_KEY")
    if not valid_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="API_KEY environment variable is not set",
        )
    if x_api_key != valid_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
        )

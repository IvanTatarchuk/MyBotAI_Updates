import os
from fastapi import Depends, HTTPException, Security
from fastapi.security.api_key import APIKeyHeader


API_KEY_HEADER = APIKeyHeader(name="x-api-key", auto_error=False)


def get_api_key_dependency(api_key: str | None = Security(API_KEY_HEADER)) -> str:
    expected_key = os.getenv("API_KEY")
    if expected_key is None:
        # Allow if unset in dev to avoid confusion
        expected_key = "dev-secret-key"
    if api_key != expected_key:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
    return expected_key


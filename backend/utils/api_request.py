import httpx
from typing import Optional, Dict, Any

async def get(url: str, body: Optional[Dict[str, Any]] = None):
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=body)
        return _handle_response(response)

async def post(url: str, body: Optional[Dict[str, Any]] = None):
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=body)
        return _handle_response(response)

async def update(url: str, body: Optional[Dict[str, Any]] = None):
    async with httpx.AsyncClient() as client:
        response = await client.put(url, json=body)
        return _handle_response(response)

async def delete(url: str, body: Optional[Dict[str, Any]] = None):
    async with httpx.AsyncClient() as client:
        response = await client.delete(url, json=body)
        return _handle_response(response)

def _handle_response(response: httpx.Response):
    if response.status_code >= 400:
        raise Exception(f"HTTP {response.status_code}: {response.text}")
    try:
        return response.json()
    except Exception:
        return response.text

import json
from fastapi.responses import StreamingResponse
import httpx
from typing import Optional, Dict, Any

request_timeout = 60.0  # 60 sec


async def get(url: str, body: Optional[Dict[str, Any]] = None):
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=body)
        return _handle_response(response)


async def post(url: str, body: Optional[Dict[str, Any]] = None):
    timeout = httpx.Timeout(request_timeout)
    async with httpx.AsyncClient(timeout=timeout) as client:
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


async def _stream_from_ai(url: str, body: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None):
    """
    Get streaming response from AI service and properly parse SSE format

    Args:
        url (str): The URL to send the request to.
        body (Optional[Dict[str, Any]]): The JSON body to send with the request.
        headers (Optional[Dict[str, str]]): Headers to send with the request.

    Yields:
        str: Parsed SSE data lines.
    """
    async with httpx.AsyncClient(timeout=60.0) as client:  # Add timeout
        async with client.stream("POST", url, json=body, headers=headers or {}) as response:
            if response.status_code != 200:
                error_text = await response.aread()
                raise Exception(f"HTTP {response.status_code}: {error_text.decode()}")
            
            async for line in response.aiter_lines():
                if line.strip():  # Only process non-empty lines
                    # SSE format: "data: {json_content}"
                    if line.startswith("data: "):
                        try:
                            json_content = line[6:]  # Remove "data: " prefix
                            # Validate JSON before yielding
                            json.loads(json_content)
                            yield line + "\n"  # Maintain SSE format
                        except json.JSONDecodeError as e:
                            print(f"JSON decode error: {e}, line: {line}")
                            continue
                    else:
                        # Pass through other SSE format lines (like comments)
                        yield line + "\n"


async def stream(ai_url: str, body: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None):
    """
    Forward streaming response to client with proper error handling.

    Args:
        ai_url (str): The URL where the AI service is hosted.
        body (Optional[Dict[str, Any]]): The JSON body to send with the request.
        headers (Optional[Dict[str, str]]): Headers to send with the request.

    Returns:
        StreamingResponse: FastAPI StreamingResponse to stream data to the client.
    """

    async def stream_response():
        try:
            print(f"Starting stream from: {ai_url}")
            print(f"Request body: {body}")
            
            async for line in _stream_from_ai(ai_url, body, headers):
                print(f"Streaming line: {line.strip()}")  # Debug logging
                yield line
                
        except Exception as e:
            print(f"Stream error: {str(e)}")  # Debug logging
            error_data = {"content": f"Error: {str(e)}", "type": "error"}
            yield f"data: {json.dumps(error_data)}\n\n"

    return StreamingResponse(
        stream_response(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/event-stream",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Allow-Methods": "*",
        },
    )


def _handle_response(response: httpx.Response):
    if response.status_code >= 400:
        raise Exception(f"HTTP {response.status_code}: {response.text}")
    try:
        return response.json()
    except Exception:
        return response.text

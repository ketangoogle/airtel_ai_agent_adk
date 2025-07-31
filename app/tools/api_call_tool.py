import requests
from typing import Optional, Dict, Any
from dotenv import load_dotenv
load_dotenv()

def make_api_call(
    method: str,
    url: str,
    headers: Optional[Dict[str, str]] = None,
    params: Optional[Dict[str, Any]] = None,
    data: Optional[Dict[str, Any]] = None) -> dict:
    """Makes an HTTP request to a specified URL."""
    try:
        response = requests.request(
            method, url, headers=headers, params=params, json=data, timeout=10
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"API call failed: {e}"}

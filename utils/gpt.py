from typing import List, Dict
import os
from openai import OpenAI

# Model and API key expected via environment variables
# MODEL = os.getenv("OPENAI_MODEL", "o4-mini")
 MODEL = st.secrets("OPENAI_MODEL", "o4-mini")

_client = None
_client_api_key = None

def get_client() -> OpenAI:
    """Return a cached OpenAI client using OPENAI_API_KEY from env.

    If the environment key changes at runtime, recreate the client.
    """
    global _client, _client_api_key
    # api_key = os.getenv("OPENAI_API_KEY")
    api_key = st.secrets("OPENAI_API_KEY")
    # Defensive: strip accidental surrounding quotes from .env entries
    if isinstance(api_key, str) and ((api_key.startswith('"') and api_key.endswith('"')) or (api_key.startswith("'") and api_key.endswith("'"))):
        api_key = api_key[1:-1]
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY not set in environment")

    # Recreate client if key changed at runtime
    if _client is None or api_key != _client_api_key:
        _client = OpenAI(api_key=api_key)
        _client_api_key = api_key
    return _client

def chat(messages: List[Dict[str, str]], temperature: float = 0.3) -> str:
    """Send a chat completion request and return assistant text.

    messages: list of {"role": "system"|"user"|"assistant", "content": "..."}
    """
    client = get_client()
    resp = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=temperature,
    )
    return resp.choices[0].message.content

__all__ = ["chat"]

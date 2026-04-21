from __future__ import annotations

import os
from typing import List, Optional


def langfuse_callbacks() -> Optional[List[object]]:
    """
    Returns Langfuse callback handler(s) if configured, else None.

    Requires env:
    - LANGFUSE_SECRET_KEY
    - LANGFUSE_PUBLIC_KEY
    - LANGFUSE_HOST (optional)
    """
    secret = os.getenv("LANGFUSE_SECRET_KEY")
    public = os.getenv("LANGFUSE_PUBLIC_KEY")
    if not secret or not public:
        return None

    try:
        # Provided by `langfuse-langchain`
        from langfuse.callback import CallbackHandler  # type: ignore
    except Exception:
        return None

    host = os.getenv("LANGFUSE_HOST")
    if host:
        return [CallbackHandler(public_key=public, secret_key=secret, host=host)]
    return [CallbackHandler(public_key=public, secret_key=secret)]

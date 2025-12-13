import threading
import time
import requests
from canva.mods.auth import auth

_token_lock = threading.Lock()
_cached_token = None
_last_refresh_attempt = 0.0
_refresh_cooldown = 60.0

def token_(client_id=None, client_secret=None, token_data="canva.json"):
    global _cached_token

    with _token_lock:
        if _cached_token is None:
            _cached_token = auth.token.get.current(token_data)
        return _cached_token


def authorized_request(
    method,
    url,
    client_id=None,
    client_secret=None,
    token_data="canva.json",
    **kwargs
):
    global _cached_token, _last_refresh_attempt

    for attempt in range(2):
        access_token = token_(client_id, client_secret, token_data)

        headers = kwargs.pop("headers", {}) or {}
        headers = {
            **headers,
            "Authorization": f"Bearer {access_token}",
        }

        resp = requests.request(method, url, headers=headers, **kwargs)

        if resp.status_code in (401, 403) and attempt == 0:
            with _token_lock:
                now = time.time()
                if now - _last_refresh_attempt < _refresh_cooldown:
                    return resp

                _last_refresh_attempt = now

                try:
                    new_token = auth.token.refresh(
                        client_id=client_id,
                        client_secret=client_secret,
                        token_data=token_data,
                    )
                except Exception as e:
                    return resp

                _cached_token = new_token
            continue

        return resp

    raise RuntimeError("authorized_request: unexpected control flow")


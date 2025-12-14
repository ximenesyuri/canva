import threading
import time
import requests
from canva.mods.auth import auth
from utils import cmd

_token_lock = threading.Lock()
_cached_token = None
_last_refresh_attempt = 0.0
_refresh_cooldown = 60.0

MAX_API_RETRIES = 5


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
    """
    Perform an HTTP request with a cached Canva access token and
    one automatic refresh on 401/403.
    """
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
                    raise

                _cached_token = new_token
            continue

        return resp

    raise RuntimeError("authorized_request: unexpected control flow")


def request_json_with_429_retry(
    method,
    url,
    client_id=None,
    client_secret=None,
    token_data="canva.json",
    max_retries=MAX_API_RETRIES,
    **kwargs
):
    last_resp = None

    for attempt in range(max_retries):
        resp = authorized_request(
            method,
            url,
            client_id=client_id,
            client_secret=client_secret,
            token_data=token_data,
            **kwargs,
        )
        last_resp = resp

        if resp.status_code == 429:
            retry_after = resp.headers.get("Retry-After")
            if retry_after is not None:
                try:
                    delay = int(retry_after)
                except ValueError:
                    delay = 2 ** attempt
            else:
                delay = 2 ** attempt

            try:
                _ = resp.json()
            except ValueError:
                _ = {"raw": resp.text}

            cmd.sleep(delay)
            continue

        try:
            body = resp.json()
        except ValueError:
            raise RuntimeError(
                f"Canva API returned non-JSON response: "
                f"status={resp.status_code}, text={resp.text}, url={url}"
            )

        if not (200 <= resp.status_code < 300):
            if (
                resp.status_code in (401, 403)
                and isinstance(body, dict)
                and body.get("code") == "invalid_access_token"
            ):
                raise RuntimeError(
                    "Canva access token is invalid. "
                    "Delete your token file and re-run the OAuth flow "
                    "(canva.init(...)) to obtain new tokens."
                )

            raise RuntimeError(
                f"Canva API error: status={resp.status_code}, body={body}, url={url}"
            )

        return body

    raise RuntimeError(
        f"Too many 429 responses from Canva API after {max_retries} attempts: "
        f"method={method}, url={url}, last_status={getattr(last_resp, 'status_code', None)}"
    )

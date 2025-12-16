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
    """
    Return a cached access token for this process, loading it from
    token_data on first use.
    """
    global _cached_token

    with _token_lock:
        if _cached_token is None:
            _cached_token = auth.token.get.current(token_data)
        return _cached_token


def _should_attempt_refresh(resp):
    """
    Decide if we should attempt an access-token refresh based on the
    HTTP response.

    We only refresh when the error indicates an invalid/expired access
    token. Permission errors or other 401/403 causes should NOT trigger
    a refresh.
    """
    if resp.status_code not in (401, 403):
        return False

    try:
        body = resp.json()
    except ValueError:
        return True

    if not isinstance(body, dict):
        return False

    code = body.get("code") or body.get("error")
    if code in ("invalid_access_token", "expired_access_token"):
        return True

    if resp.status_code == 401 and code is None:
        return True

    return False


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
    one automatic refresh on 401/403 only when the response indicates
    the access token is invalid/expired.

    This, combined with the cross-process lock in auth.token.refresh(),
    avoids concurrent reuse of the same refresh token (which would cause
    Canva to revoke the entire token lineage).
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
            if not _should_attempt_refresh(resp):
                return resp

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
                except Exception:
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
    """
    Wrapper around authorized_request that:
    - Retries on 429 with exponential backoff (respecting Retry-After).
    - Parses JSON responses.
    - Raises descriptive RuntimeError on Canva API errors.
    """
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
                "Canva API returned non-JSON response: "
                f"status={resp.status_code}, text={resp.text}, url={url}"
            )

        if not (200 <= resp.status_code < 300):
            if (
                resp.status_code in (401, 403)
                and isinstance(body, dict)
                and body.get("code") == "invalid_access_token"
            ):
                raise RuntimeError(
                    "Canva access token is invalid even after refresh. "
                    "Delete your token file and re-run the OAuth flow "
                    "(canva.init(...)) to obtain new tokens."
                )

            raise RuntimeError(
                f"Canva API error: status={resp.status_code}, body={body}, url={url}"
            )

        return body

    raise RuntimeError(
        "Too many 429 responses from Canva API after "
        f"{max_retries} attempts: method={method}, url={url}, "
        f"last_status={getattr(last_resp, 'status_code', None)}"
    )


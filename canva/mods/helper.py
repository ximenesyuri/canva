import threading
import requests
from canva.mods.auth import auth

_token_lock = threading.Lock()
_cached_token = None

def token_(client_id=None, client_secret=None, token_data="canva.json"):
    global _cached_token

    if _cached_token is None:
        _cached_token = auth.token.get.current(token_data)

    url = 'https://api.canva.com/rest/v1/designs'
    headers = {
        'Authorization': f'Bearer {_cached_token}'
    }
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return _cached_token

    if response.status_code in (401, 403):
        with _token_lock:
            headers = {'Authorization': f'Bearer {_cached_token}'}
            check = requests.get(url, headers=headers)
            if check.status_code == 200:
                return _cached_token

            new_token = auth.token.refresh(client_id, client_secret, token_data)
            _cached_token = new_token
            return _cached_token

    raise RuntimeError(
        f"Canva /designs probe returned {response.status_code}: {response.text}"
    )


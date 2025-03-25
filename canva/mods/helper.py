from canva.mods.auth import auth
import requests

def token_(client_id=None,  client_secret=None, token_file="canva.json"):
    current_token = auth.token.get.current(client_id, client_secret, token_file)
    url = 'https://api.canva.com/rest/v1/designs'
    headers = {
        'Authorization': f'Bearer {current_token}'
    }
    response = requests.get(url, headers=headers)
    if response.status_code == '200':
        return current_token
    else:
        return auth.token.refresh(client_id,  client_secret, token_file)

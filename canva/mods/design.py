from canva.mods.auth import auth
import requests

class design:
    def list(client_id, client_secret, token_file="canva.json"):
        access_token = auth.token.refresh(client_id, client_secret, token_file)

        url = 'https://api.canva.com/rest/v1/designs'
        headers = {
            'Authorization': f'Bearer {access_token}'
        }

        return requests.get(url, headers=headers).json()


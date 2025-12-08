from canva.mods.helper import token_
import requests

class page:
    def list(design_id, offset=1, limit=200, client_id=None, client_secret=None, token_data="canva.json"): 
        access_token = token_(client_id, client_secret, token_data)
        url = f'https://api.canva.com/rest/v1/designs/{design_id}/pages?offset={offset}&limit={limit}'
        headers = {
            'Authorization': f'Bearer {access_token}'
        }

        return requests.get(url, headers=headers).json()

    class get:
        def all(design_id, page_index=1, client_id=None, client_secret=None, token_data="canva.json"):
            pages = page.list(design_id, 1, 200, client_id, client_secret, token_data)
            for p in pages['items']:
                if p['index'] == page_index:
                    return p
            return None

        def geometry(design_id, page_index=1, client_id=None, client_secret=None, token_data="canva.json"):
            p = page.get.all(design_id, page_index, client_id, client_secret, token_data)
            return {'width': p['thumbnail']['width'], 'height': p['thumbnail']['height']}

        def url(design_id, page_index=1, client_id=None, client_secret=None, token_data="canva.json"):
            p = page.get.all(design_id, page_index, client_id, client_secret, token_data)
            return p['thumbnail']['url']

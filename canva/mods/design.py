from canva.mods.helper import token_
import requests

class design:
    def list(client_id=None, client_secret=None, token_data="canva.json"):
        access_token = token_(client_id, client_secret, token_data)

        url = 'https://api.canva.com/rest/v1/designs'
        headers = {
            'Authorization': f'Bearer {access_token}'
        }

        return requests.get(url, headers=headers).json()

    class get:
        def id(design_name, client_id=None, client_secret=None, token_data="canva.json"):
            designs = design.list(client_id, client_secret, token_data)
            for d in designs['items']:
                if d['title'] == design_name:
                    return d['id']
            return None

        def all(design_id, client_id=None, client_secret=None, token_data="canva.json"):
            access_token = token_(client_id, client_secret, token_data)
            url = f'https://api.canva.com/rest/v1/designs/{design_id}'
            headers = {
                'Authorization': f'Bearer {access_token}'
            }
            return requests.get(url, headers=headers).json()

        class thumb:
            def all(design_id, client_id=None, client_secret=None, token_data="canva.json"):
               info = design.get.all(design_id, client_id, client_secret, token_data)
               return info['design']['thumbnail']

            def geometry(design_id, client_id=None, client_secret=None, token_data="canva.json"):
               thumb = design.get.thumb.all(design_id, client_id, client_secret, token_data)
               return {'width': thumb['width'], 'height': thumb['height']}

            def url(design_id, client_id=None, client_secret=None, token_data="canva.json"):
                thumb = design.get.thumb.all(design_id, client_id, client_secret, token_data)
                return thumb['url']

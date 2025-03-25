from canva.mods.helper import token_
import requests

class design:
    def list(client_id=None, client_secret=None, token_file="canva.json"):
        access_token = token_(client_id, client_secret, token_file)

        url = 'https://api.canva.com/rest/v1/designs'
        headers = {
            'Authorization': f'Bearer {access_token}'
        }

        return requests.get(url, headers=headers).json()

    class get:
        def id(design_name, client_id=None, client_secret=None, token_file="canva.json"):
            designs = design.list(client_id, client_secret, token_file)
            for d in designs['items']:
                if d['title'] == design_name:
                    return d['id']
            return None

        def all(design_id, client_id=None, client_secret=None, token_file="canva.json"):
            access_token = token_(client_id, client_secret, token_file)
            url = f'https://api.canva.com/rest/v1/designs/{design_id}'
            headers = {
                'Authorization': f'Bearer {access_token}'
            }
            return requests.get(url, headers=headers).json()

        class thumb:
            def all(design_id, client_id=None, client_secret=None, token_file="canva.json"):
               info = design.get.all(design_id, client_id, client_secret, token_file)
               return info['design']['thumbnail']

            def geometry(design_id, client_id=None, client_secret=None, token_file="canva.json"):
               thumb = design.get.thumb.all(design_id, client_id, client_secret, token_file)
               return {'width': thumb['width'], 'height': thumb['height']}

            def url(design_id, client_id=None, client_secret=None, token_file="canva.json"):
                thumb = design.get.thumb.all(design_id, client_id, client_secret, token_file)
                return thumb['url']

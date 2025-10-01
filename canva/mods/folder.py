from canva.mods.helper import token_
import requests

class folder:
    class list:
        def designs(parent_id, client_id=None, client_secret=None, token_file="canva.json"):
            access_token = token_(client_id, client_secret, token_file)
            url = f'https://api.canva.com/rest/v1/folders/{parent_id}/items'
            headers = {
                'Authorization': f'Bearer {access_token}'
            }
            response = requests.get(url, headers=headers).json()
            items = []
            items.extend(response.get('items', []))
            continuation = response.get('continuation', '')
            while continuation:
                url = f'https://api.canva.com/rest/v1/folders/{parent_id}/items?continuation={continuation}'
                response = requests.get(url, headers=headers).json()
                items.extend(response.get('items', []))
                continuation = response.get('continuation', '')
            return items

        def folders(parent_id, client_id=None, client_secret=None, token_file="canva.json"):
            access_token = token_(client_id, client_secret, token_file)
            url = f'https://api.canva.com/rest/v1/folders/{parent_id}/items?item_types=folder'
            headers = {
                'Authorization': f'Bearer {access_token}'
            }
            response = requests.get(url, headers=headers).json()
            items = []
            items.extend(response.get('items', []))
            continuation = response.get('continuation', '')
            while continuation:
                url = f'https://api.canva.com/rest/v1/folders/{parent_id}/items?continuation={continuation}'
                response = requests.get(url, headers=headers).json()
                items.extend(response.get('items', []))
                continuation = response.get('continuation', '')
            return items

        def designs(parent_id, client_id=None, client_secret=None, token_file="canva.json"):
            access_token = token_(client_id, client_secret, token_file)
            url = f'https://api.canva.com/rest/v1/folders/{parent_id}/items?item_types=design'
            headers = {
                'Authorization': f'Bearer {access_token}'
            }
            response = requests.get(url, headers=headers).json()
            items = []
            items.extend(response.get('items', []))
            continuation = response.get('continuation', '')
            while continuation:
                url = f'https://api.canva.com/rest/v1/folders/{parent_id}/items?continuation={continuation}'
                response = requests.get(url, headers=headers).json()
                items.extend(response.get('items', []))
                continuation = response.get('continuation', '')
            return items

    class get:
        def id(folder_name, parent_id, client_id=None, client_secret=None, token_file="canva.json"):
            folders = folder.list.folders(client_id, client_secret, token_file)
            for f in folders['items']:
                if f['folder']['name'] == folder_name:
                    return f['id']
            return None

        def all(folder_id, client_id=None, client_secret=None, token_file="canva.json"):
            access_token = token_(client_id, client_secret, token_file)
            url = f'https://api.canva.com/rest/v1/folders/{folder_id}'
            headers = {
                'Authorization': f'Bearer {access_token}'
            }
            return requests.get(url, headers=headers).json()

        class thumb:
            def all(folder_id, client_id=None, client_secret=None, token_file="canva.json"):
               info = folder.get.all(folder_id, client_id, client_secret, token_file)
               return info['folder']['thumbnail']

            def geometry(folder_id, client_id=None, client_secret=None, token_file="canva.json"):
               thumb = folder.get.thumb.all(folder_id, client_id, client_secret, token_file)
               return {'width': thumb['width'], 'height': thumb['height']}

            def url(folder_id, client_id=None, client_secret=None, token_file="canva.json"):
                thumb = folder.get.thumb.all(folder_id, client_id, client_secret, token_file)
                return thumb['url']

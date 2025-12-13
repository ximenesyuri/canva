import requests
from canva.mods.helper import token_
from canva.mods.design import design

class export:
    class design:
        def png(design_id, bg=False, client_id=None, client_secret=None, token_data="canva.json"):
            access_token = token_(client_id, client_secret, token_data)
            url = 'https://api.canva.com/rest/v1/exports'
            headers = {
                'Authorization': f'Bearer {access_token}',
                "Content-Type": "application/json"
            }
            data = {
                "design_id": design_id,
                "format": {
                    "type": "png",
                    "transparent_background": bg
                }
            }
            resp = requests.post(url, headers=headers, json=data)

            try:
                body = resp.json()
            except ValueError:
                raise RuntimeError(
                    f"Canva export PNG returned non-JSON response: "
                    f"status={resp.status_code}, text={resp.text}"
                )

            if 'job' not in body or 'id' not in body['job']:
                raise RuntimeError(
                    f"Unexpected Canva export PNG response: "
                    f"status={resp.status_code}, body={body}"
                )

            return body['job']['id']

        def svg(design_id, bg=False, client_id=None, client_secret=None, token_data="canva.json"):
            access_token = token_(client_id, client_secret, token_data)
            url = f'https://api.canva.com/rest/v1/exports'
            headers = {
                'Authorization': f'Bearer {access_token}',
                "Content-Type": "application/json"
            }
            data = {
                "design_id": design_id,
                "format": {
                    "type": "svg",
                    "transparent_background": bg
                }
            }
            return requests.post(url, headers=headers, json=data).json()['job']['id']

        def jpg(design_id, bg=False, client_id=None, client_secret=None, token_data="canva.json"):
            access_token = token_(client_id, client_secret, token_data)
            url = f'https://api.canva.com/rest/v1/exports'
            headers = {
                'Authorization': f'Bearer {access_token}',
                "Content-Type": "application/json"
            }
            data = {
                "design_id": design_id,
                "format": {
                    "type": "jpg",
                    "transparent_background": bg
                }
            }
            return requests.post(url, headers=headers, json=data).json()['job']['id']
        jpeg = jpg

    class pages:
        def png(design_id, page_indexes=[1], bg=False, client_id=None, client_secret=None, token_data="canva.json"):
            access_token = token_(client_id, client_secret, token_data)
            url = f'https://api.canva.com/rest/v1/exports'
            headers = {
                'Authorization': f'Bearer {access_token}',
                "Content-Type": "application/json"
            }
            data = {
                "design_id": design_id,
                "format": {
                    "type": "png",
                    "pages": page_indexes,
                    "transparent_background": bg
                }
            }
            return requests.post(url, headers=headers, json=data).json()['job']['id']

        def svg(design_id, page_indexes=[1], bg=False, client_id=None, client_secret=None, token_data="canva.json"):
            access_token = token_(client_id, client_secret, token_data)
            url = f'https://api.canva.com/rest/v1/exports'
            headers = {
                'Authorization': f'Bearer {access_token}',
                "Content-Type": "application/json"
            }
            data = {
                "design_id": design_id,
                "format": {
                    "type": "svg",
                    "pages": page_indexes,
                    "transparent_background": bg
                }
            }
            return requests.post(url, headers=headers, json=data).json()['job']['id']

        def jpg(design_id, page_indexes=[1], bg=False, client_id=None, client_secret=None, token_data="canva.json"):
            access_token = token_(client_id, client_secret, token_data)
            url = f'https://api.canva.com/rest/v1/exports'
            headers = {
                'Authorization': f'Bearer {access_token}',
                "Content-Type": "application/json"
            }
            data = {
                "design_id": design_id,
                "format": {
                    "type": "jpg",
                    "pages": page_indexes,
                    "transparent_background": bg
                }
            }
            return requests.post(url, headers=headers, json=data).json()['job']['id']
        jpeg = jpg

    class get:
        def all(export_id, client_id=None, client_secret=None, token_data="canva.json"):
            access_token = token_(client_id, client_secret, token_data)
            url = f'https://api.canva.com/rest/v1/exports/{export_id}'
            headers = {
                'Authorization': f'Bearer {access_token}'
            }
            return requests.get(url, headers=headers).json()['job']

        def status(export_id, client_id=None, client_secret=None, token_data="canva.json"):
            e = export.get.all(export_id, client_id, client_secret, token_data)
            return e['status']

        def url(export_id, client_id=None, client_secret=None, token_data="canva.json"):
            e = export.get.all(export_id, client_id, client_secret, token_data)
            return e['urls']

import requests
from canva.mods.helper import token_
from canva.mods.design import design

class export:
    class design:
        def png(design_id, bg=False, client_id=None, client_secret=None, token_file="canva.json"):
            access_token = token_(client_id, client_secret, token_file)
            url = f'https://api.canva.com/rest/v1/exports'
            headers = {
                'Authorization': f'Bearer {access_token}',
                "Content-Type": "application/json"
            }
            #geometry = design.get.thumb.geometry(design_id, client_id, client_secret, token_file)
            data = {
                "design_id": design_id,
                "format": {
                    "type": "png",
                    #"width": f"{geometry['width']}",
                    #"height": f"{geometry['height']}",
                    "transparent_background": bg
                }
            }
            return requests.post(url, headers=headers, json=data).json()['job']['id']

        def svg(design_id, bg=False, client_id=None, client_secret=None, token_file="canva.json"):
            access_token = token_(client_id, client_secret, token_file)
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

        def jpg(design_id, bg=False, client_id=None, client_secret=None, token_file="canva.json"):
            access_token = token_(client_id, client_secret, token_file)
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
        def png(design_id, page_indexes=[1], bg=False, client_id=None, client_secret=None, token_file="canva.json"):
            access_token = token_(client_id, client_secret, token_file)
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

        def svg(design_id, page_indexes=[1], bg=False, client_id=None, client_secret=None, token_file="canva.json"):
            access_token = token_(client_id, client_secret, token_file)
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

        def jpg(design_id, page_indexes=[1], bg=False, client_id=None, client_secret=None, token_file="canva.json"):
            access_token = token_(client_id, client_secret, token_file)
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
        def all(export_id, client_id=None, client_secret=None, token_file="canva.json"):
            access_token = token_(client_id, client_secret, token_file)
            url = f'https://api.canva.com/rest/v1/exports/{export_id}'
            headers = {
                'Authorization': f'Bearer {access_token}'
            }
            return requests.get(url, headers=headers).json()['job']

        def status(export_id, client_id=None, client_secret=None, token_file="canva.json"):
            e = export.get.all(export_id, client_id, client_secret, token_file)
            return e['status']

        def url(export_id, client_id=None, client_secret=None, token_file="canva.json"):
            e = export.get.all(export_id, client_id, client_secret, token_file)
            return e['urls']

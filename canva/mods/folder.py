from canva.mods.helper import request_json_with_429_retry

class folder:
    class list:
        @staticmethod
        def all(parent_id, client_id=None, client_secret=None, token_data="canva.json"):
            base_url = f"https://api.canva.com/rest/v1/folders/{parent_id}/items"

            response = request_json_with_429_retry(
                "GET",
                base_url,
                client_id=client_id,
                client_secret=client_secret,
                token_data=token_data,
            )

            items = []
            items.extend(response.get("items", []))
            continuation = response.get("continuation", "")

            while continuation:
                url = f"{base_url}?continuation={continuation}"
                response = request_json_with_429_retry(
                    "GET",
                    url,
                    client_id=client_id,
                    client_secret=client_secret,
                    token_data=token_data,
                )
                items.extend(response.get("items", []))
                continuation = response.get("continuation", "")

            return items

        @staticmethod
        def folders(parent_id, client_id=None, client_secret=None, token_data="canva.json"):
            base_url = (
                f"https://api.canva.com/rest/v1/folders/{parent_id}/items?item_types=folder"
            )

            response = request_json_with_429_retry(
                "GET",
                base_url,
                client_id=client_id,
                client_secret=client_secret,
                token_data=token_data,
            )

            items = []
            items.extend(response.get("items", []))
            continuation = response.get("continuation", "")

            while continuation:
                url = f"https://api.canva.com/rest/v1/folders/{parent_id}/items?continuation={continuation}"
                response = request_json_with_429_retry(
                    "GET",
                    url,
                    client_id=client_id,
                    client_secret=client_secret,
                    token_data=token_data,
                )
                items.extend(response.get("items", []))
                continuation = response.get("continuation", "")

            return items

        @staticmethod
        def designs(parent_id, client_id=None, client_secret=None, token_data="canva.json"):
            try:
                base_url = (
                    f"https://api.canva.com/rest/v1/folders/{parent_id}/items?item_types=design"
                )

                response = request_json_with_429_retry(
                    "GET",
                    base_url,
                    client_id=client_id,
                    client_secret=client_secret,
                    token_data=token_data,
                )

                items = []
                items.extend(response.get("items", []))
                continuation = response.get("continuation", "")

                while continuation:
                    url = f"https://api.canva.com/rest/v1/folders/{parent_id}/items?continuation={continuation}"
                    response = request_json_with_429_retry(
                        "GET",
                        url,
                        client_id=client_id,
                        client_secret=client_secret,
                        token_data=token_data,
                    )
                    items.extend(response.get("items", []))
                    continuation = response.get("continuation", "")

                return items
            except Exception as e:
                raise RuntimeError(e)

    class get:
        @staticmethod
        def id(folder_name, parent_id, client_id=None, client_secret=None, token_data="canva.json"):
            folders_list = folder.list.folders(parent_id, client_id, client_secret, token_data)
            for f in folders_list:
                if f.get("folder", {}).get("name") == folder_name:
                    return f.get("id")
            return None

        @staticmethod
        def all(folder_id, client_id=None, client_secret=None, token_data="canva.json"):
            url = f"https://api.canva.com/rest/v1/folders/{folder_id}"

            body = request_json_with_429_retry(
                "GET",
                url,
                client_id=client_id,
                client_secret=client_secret,
                token_data=token_data,
            )

            return body

        class thumb:
            @staticmethod
            def all(folder_id, client_id=None, client_secret=None, token_data="canva.json"):
                info = folder.get.all(folder_id, client_id, client_secret, token_data)
                return info["folder"]["thumbnail"]

            @staticmethod
            def geometry(folder_id, client_id=None, client_secret=None, token_data="canva.json"):
                thumb = folder.get.thumb.all(folder_id, client_id, client_secret, token_data)
                return {"width": thumb["width"], "height": thumb["height"]}

            @staticmethod
            def url(folder_id, client_id=None, client_secret=None, token_data="canva.json"):
                thumb = folder.get.thumb.all(folder_id, client_id, client_secret, token_data)
                return thumb["url"]


from canva.mods.helper import request_json_with_429_retry

class page:
    @staticmethod
    def list(
        design_id,
        offset=1,
        limit=200,
        client_id=None,
        client_secret=None,
        token_data="canva.json",
    ):
        url = f"https://api.canva.com/rest/v1/designs/{design_id}/pages?offset={offset}&limit={limit}"

        body = request_json_with_429_retry(
            "GET",
            url,
            client_id=client_id,
            client_secret=client_secret,
            token_data=token_data,
        )

        return body

    class get:
        @staticmethod
        def all(
            design_id,
            page_index=1,
            client_id=None,
            client_secret=None,
            token_data="canva.json",
        ):
            pages = page.list(design_id, 1, 200, client_id, client_secret, token_data)
            for p in pages.get("items", []):
                if p.get("index") == page_index:
                    return p
            return None

        @staticmethod
        def geometry(
            design_id,
            page_index=1,
            client_id=None,
            client_secret=None,
            token_data="canva.json",
        ):
            p = page.get.all(design_id, page_index, client_id, client_secret, token_data)
            return {
                "width": p["thumbnail"]["width"],
                "height": p["thumbnail"]["height"],
            }

        @staticmethod
        def url(
            design_id,
            page_index=1,
            client_id=None,
            client_secret=None,
            token_data="canva.json",
        ):
            p = page.get.all(design_id, page_index, client_id, client_secret, token_data)
            return p["thumbnail"]["url"]


from canva.mods.helper import request_json_with_429_retry

class design:
    @staticmethod
    def list(client_id=None, client_secret=None, token_data="canva.json"):
        url = "https://api.canva.com/rest/v1/designs"

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
        def id(design_name, client_id=None, client_secret=None, token_data="canva.json"):
            designs = design.list(client_id, client_secret, token_data)
            for d in designs.get("items", []):
                if d.get("title") == design_name:
                    return d.get("id")
            return None

        @staticmethod
        def all(design_id, client_id=None, client_secret=None, token_data="canva.json"):
            url = f"https://api.canva.com/rest/v1/designs/{design_id}"

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
            def all(design_id, client_id=None, client_secret=None, token_data="canva.json"):
                info = design.get.all(design_id, client_id, client_secret, token_data)
                return info["design"]["thumbnail"]

            @staticmethod
            def geometry(design_id, client_id=None, client_secret=None, token_data="canva.json"):
                thumb = design.get.thumb.all(design_id, client_id, client_secret, token_data)
                return {"width": thumb["width"], "height": thumb["height"]}

            @staticmethod
            def url(design_id, client_id=None, client_secret=None, token_data="canva.json"):
                thumb = design.get.thumb.all(design_id, client_id, client_secret, token_data)
                return thumb["url"]


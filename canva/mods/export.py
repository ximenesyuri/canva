from canva.mods.helper import authorized_request, request_json_with_429_retry
from canva.mods.design import design
from utils import cmd

MAX_EXPORT_RETRIES = 5


class export:
    class design:
        @staticmethod
        def png(design_id, bg=False, client_id=None, client_secret=None, token_data="canva.json"):
            url = "https://api.canva.com/rest/v1/exports"
            data = {
                "design_id": design_id,
                "format": {
                    "type": "png",
                    "transparent_background": bg,
                },
            }

            for attempt in range(MAX_EXPORT_RETRIES):
                resp = authorized_request(
                    "POST",
                    url,
                    client_id=client_id,
                    client_secret=client_secret,
                    token_data=token_data,
                    json=data,
                    headers={"Content-Type": "application/json"},
                )

                if resp.status_code == 429:
                    retry_after = resp.headers.get("Retry-After")
                    if retry_after is not None:
                        try:
                            delay = int(retry_after)
                        except ValueError:
                            delay = 2 ** attempt
                    else:
                        delay = 2 ** attempt

                    try:
                        _ = resp.json()
                    except ValueError:
                        _ = {"raw": resp.text}

                    cmd.sleep(delay)
                    continue

                try:
                    body = resp.json()
                except ValueError:
                    raise RuntimeError(
                        f"Canva export PNG returned non-JSON response: "
                        f"status={resp.status_code}, text={resp.text}"
                    )

                if "job" not in body or "id" not in body["job"]:
                    raise RuntimeError(
                        f"Unexpected Canva export PNG response: "
                        f"status={resp.status_code}, body={body}"
                    )

                return body["job"]["id"]

            raise RuntimeError(
                f"Too many 429 responses from Canva export PNG after {MAX_EXPORT_RETRIES} attempts"
            )

        @staticmethod
        def svg(design_id, bg=False, client_id=None, client_secret=None, token_data="canva.json"):
            url = "https://api.canva.com/rest/v1/exports"
            data = {
                "design_id": design_id,
                "format": {
                    "type": "svg",
                    "transparent_background": bg,
                },
            }

            body = request_json_with_429_retry(
                "POST",
                url,
                client_id=client_id,
                client_secret=client_secret,
                token_data=token_data,
                json=data,
                headers={"Content-Type": "application/json"},
            )

            if "job" not in body or "id" not in body["job"]:
                raise RuntimeError(
                    f"Unexpected Canva export SVG response: body={body}"
                )

            return body["job"]["id"]

        @staticmethod
        def jpg(design_id, bg=False, client_id=None, client_secret=None, token_data="canva.json"):
            url = "https://api.canva.com/rest/v1/exports"
            data = {
                "design_id": design_id,
                "format": {
                    "type": "jpg",
                    "transparent_background": bg,
                },
            }

            body = request_json_with_429_retry(
                "POST",
                url,
                client_id=client_id,
                client_secret=client_secret,
                token_data=token_data,
                json=data,
                headers={"Content-Type": "application/json"},
            )

            if "job" not in body or "id" not in body["job"]:
                raise RuntimeError(
                    f"Unexpected Canva export JPG response: body={body}"
                )

            return body["job"]["id"]

        jpeg = jpg

    class pages:
        @staticmethod
        def png(
            design_id,
            page_indexes=[1],
            bg=False,
            client_id=None,
            client_secret=None,
            token_data="canva.json",
        ):
            url = "https://api.canva.com/rest/v1/exports"
            data = {
                "design_id": design_id,
                "format": {
                    "type": "png",
                    "pages": page_indexes,
                    "transparent_background": bg,
                },
            }

            body = request_json_with_429_retry(
                "POST",
                url,
                client_id=client_id,
                client_secret=client_secret,
                token_data=token_data,
                json=data,
                headers={"Content-Type": "application/json"},
            )

            if "job" not in body or "id" not in body["job"]:
                raise RuntimeError(
                    f"Unexpected Canva export pages PNG response: body={body}"
                )

            return body["job"]["id"]

        @staticmethod
        def svg(
            design_id,
            page_indexes=[1],
            bg=False,
            client_id=None,
            client_secret=None,
            token_data="canva.json",
        ):
            url = "https://api.canva.com/rest/v1/exports"
            data = {
                "design_id": design_id,
                "format": {
                    "type": "svg",
                    "pages": page_indexes,
                    "transparent_background": bg,
                },
            }

            body = request_json_with_429_retry(
                "POST",
                url,
                client_id=client_id,
                client_secret=client_secret,
                token_data=token_data,
                json=data,
                headers={"Content-Type": "application/json"},
            )

            if "job" not in body or "id" not in body["job"]:
                raise RuntimeError(
                    f"Unexpected Canva export pages SVG response: body={body}"
                )

            return body["job"]["id"]

        @staticmethod
        def jpg(
            design_id,
            page_indexes=[1],
            bg=False,
            client_id=None,
            client_secret=None,
            token_data="canva.json",
        ):
            url = "https://api.canva.com/rest/v1/exports"
            data = {
                "design_id": design_id,
                "format": {
                    "type": "jpg",
                    "pages": page_indexes,
                    "transparent_background": bg,
                },
            }

            body = request_json_with_429_retry(
                "POST",
                url,
                client_id=client_id,
                client_secret=client_secret,
                token_data=token_data,
                json=data,
                headers={"Content-Type": "application/json"},
            )

            if "job" not in body or "id" not in body["job"]:
                raise RuntimeError(
                    f"Unexpected Canva export pages JPG response: body={body}"
                )

            return body["job"]["id"]

        jpeg = jpg

    class get:
        @staticmethod
        def all(export_id, client_id=None, client_secret=None, token_data="canva.json"):
            url = f"https://api.canva.com/rest/v1/exports/{export_id}"

            body = request_json_with_429_retry(
                "GET",
                url,
                client_id=client_id,
                client_secret=client_secret,
                token_data=token_data,
            )

            if "job" not in body:
                raise RuntimeError(
                    f"Unexpected Canva export get response: body={body}"
                )

            return body["job"]

        @staticmethod
        def status(export_id, client_id=None, client_secret=None, token_data="canva.json"):
            e = export.get.all(export_id, client_id, client_secret, token_data)
            return e["status"]

        @staticmethod
        def url(export_id, client_id=None, client_secret=None, token_data="canva.json"):
            e = export.get.all(export_id, client_id, client_secret, token_data)
            return e["urls"]


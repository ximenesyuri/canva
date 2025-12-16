import os
import time
import requests
import base64
import hashlib
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from contextlib import contextmanager

from typed import typed, Str, Nill, Dict, Path, Maybe, Union, File, Tuple
from utils import file, json, envs, cmd

try:
    import fcnt
    _HAS_FCNTL = True
except ImportError:
    fcntl = None
    _HAS_FCNTL = False


def collect_after_sequence(input_string, sequence):
    index = input_string.find(sequence)
    if index != -1:
        return input_string[index + len(sequence):]
    else:
        return None

def _token_lock_path(token_data) -> str:
    base = str(token_data)
    return base + ".lock"

@contextmanager
def _token_file_lock(token_data):
    lock_path = _token_lock_path(token_data)
    dir_name = os.path.dirname(lock_path)
    if dir_name:
        os.makedirs(dir_name, exist_ok=True)

    f = open(lock_path, "a+")

    try:
        if _HAS_FCNTL:
            fcntl.flock(f, fcntl.LOCK_EX)
        yield
    finally:
        if _HAS_FCNTL:
            fcntl.flock(f, fcntl.LOCK_UN)
        f.close()


class auth:
    class scopes:
        @staticmethod
        def read():
            return (
                "app:read%20"
                "design:content:read%20"
                "design:meta:read%20"
                "design:permission:read%20"
                "folder:read%20"
                "folder:permission:read%20"
                "asset:read%20"
                "comment:read%20"
                "brandtemplate:meta:read%20"
                "brandtemplate:content:read%20"
                "profile:read"
            )

        @staticmethod
        def write():
            return (
                "app:read%20app:write%20"
                "design:content:read%20"
                "design:meta:read%20"
                "design:content:write%20"
                "design:permission:read%20"
                "design:permission:write%20"
                "folder:read%20"
                "folder:write%20"
                "folder:permission:read%20"
                "folder:permission:write%20"
                "asset:read%20"
                "asset:write%20"
                "comment:read%20"
                "comment:write%20"
                "brandtemplate:meta:read%20"
                "brandtemplate:content:read%20"
                "profile:read"
            )

    class code:
        @staticmethod
        def verifier():
            return (
                base64.urlsafe_b64encode(os.urandom(32))
                .rstrip(b"=")
                .decode("utf-8")
            )

        @staticmethod
        def challenge(code_verifier):
            code_challenge = hashlib.sha256(code_verifier.encode()).digest()
            return (
                base64.urlsafe_b64encode(code_challenge)
                .rstrip(b"=")
                .decode("utf-8")
            )

    class token:
        class get:
            @typed
            def new(
                client_id: Maybe(Str) = None,
                client_secret: Maybe(Str) = None,
                scopes: Maybe(Str) = None,
                token_data: Union(Dict, Path) = "canva.json",
            ) -> Maybe(Tuple):
                """
                Perform the OAuth authorization code + PKCE flow and store
                new access/refresh tokens into token_data (file or dict).

                Returns (access_token, refresh_token) when successful,
                or None if something failed.
                """
                if not client_id:
                    client_id = envs.get("CANVA_CLIENT_ID")
                    if not client_id:
                        raise ValueError("Client ID not provided.")

                if not client_secret:
                    client_secret = envs.get("CANVA_CLIENT_SECRET")
                    if not client_secret:
                        raise ValueError("Client Secret not provided.")

                if scopes is None:
                    scopes = auth.scopes.read()

                access_token = ""
                refresh_token = ""

                if token_data in Path:
                    cmd.touch(token_data)
                    try:
                        token_data_ = json.read(token_data)
                        access_token = token_data_.get("access_token")
                        refresh_token = token_data_.get("refresh_token")
                    except Exception:
                        pass

                if token_data in Dict:
                    access_token = token_data.get("access_token")
                    refresh_token = token_data.get("refresh_token")

                if access_token and refresh_token:
                    return access_token, refresh_token

                code_verifier = auth.code.verifier()
                code_challenge = auth.code.challenge(code_verifier)

                redirect_uri = "http://127.0.0.1:8080"
                authorization_url = (
                    "https://www.canva.com/api/oauth/authorize?"
                    f"response_type=code&client_id={client_id}"
                    f"&redirect_uri={redirect_uri}"
                    f"&scope={scopes}"
                    f"&code_challenge={code_challenge}"
                    f"&code_challenge_method=S256"
                )

                webbrowser.open(authorization_url)

                class OAuthHandler(BaseHTTPRequestHandler):
                    def do_GET(self_):
                        query = urlparse(self_.path).query
                        params = parse_qs(query)
                        auth_code = params.get("code", [None])[0]

                        self_.send_response(200)
                        self_.send_header("Content-type", "text/html")
                        self_.end_headers()
                        self_.wfile.write(
                            b"Thank you! You have authorized the app. "
                            b"You can now close this window."
                        )

                        self_.server.auth_code = auth_code

                with HTTPServer(("127.0.0.1", 8080), OAuthHandler) as httpd:
                    print("Listening for authorization code...")
                    httpd.handle_request()

                auth_code = getattr(httpd, "auth_code", None)
                if not auth_code:
                    raise ValueError("Failed to obtain authorization code.")

                token_url = "https://api.canva.com/rest/v1/oauth/token"
                credentials = f"{client_id}:{client_secret}"
                encoded_credentials = base64.b64encode(credentials.encode()).decode()

                headers = {
                    "Authorization": f"Basic {encoded_credentials}",
                    "Content-Type": "application/x-www-form-urlencoded",
                }

                data = {
                    "grant_type": "authorization_code",
                    "code": auth_code,
                    "redirect_uri": redirect_uri,
                    "code_verifier": code_verifier,
                }

                response = requests.post(token_url, headers=headers, data=data)

                if response.status_code == 200:
                    token_data_ = response.json()
                    access_token = token_data_.get("access_token")
                    refresh_token = token_data_.get("refresh_token")
                    expires_in = token_data_.get("expires_in")

                    token_dict = {
                        "access_token": access_token,
                        "refresh_token": refresh_token,
                    }
                    if expires_in is not None:
                        try:
                            expires_in_int = int(expires_in)
                        except (TypeError, ValueError):
                            expires_in_int = None
                        if expires_in_int:
                            token_dict["expires_in"] = expires_in_int
                            token_dict["expires_at"] = (
                                time.time() + expires_in_int - 60
                            )

                    if token_data in Path:
                        with _token_file_lock(token_data):
                            json.write(token_dict, token_data)

                    if token_data in Dict:
                        token_data.update(token_dict)

                    print("Tokens saved to token storage")
                    return access_token, refresh_token

                else:
                    print("Error:", response.status_code)
                    print("Response:", response.text)
                    return None

            @typed
            def current(token_data: Union(File, Dict)) -> Str:
                """
                Return the current access token from token_data (file or dict).
                """
                if token_data in File:
                    data = json.read(token_data)
                    current_token = data.get("access_token")
                    if current_token:
                        return current_token
                    raise ValueError(
                        f"There is no access token defined in {token_data}."
                    )

                if token_data in Dict:
                    current_token = token_data.get("access_token")
                    if current_token:
                        return current_token
                    raise ValueError(
                        "There is no access token defined in in-memory token_data."
                    )

        @typed
        def refresh(
            client_id: Maybe(Str) = None,
            client_secret: Maybe(Str) = None,
            token_data: Union(File, Dict) = "canva.json",
        ) -> Str:

            if not client_id:
                client_id = envs.get("CANVA_CLIENT_ID")
                if not client_id:
                    raise ValueError("Client ID not provided for refresh().")

            if not client_secret:
                client_secret = envs.get("CANVA_CLIENT_SECRET")
                if not client_secret:
                    raise ValueError("Client Secret not provided for refresh().")

            token_url = "https://api.canva.com/rest/v1/oauth/token"
            credentials = f"{client_id}:{client_secret}"
            encoded_credentials = base64.b64encode(credentials.encode()).decode()

            headers = {
                "Authorization": f"Basic {encoded_credentials}",
                "Content-Type": "application/x-www-form-urlencoded",
            }

            if token_data in File:
                with _token_file_lock(token_data):
                    token_data_ = json.read(token_data)
                    refresh_token = token_data_.get("refresh_token")
                    if not refresh_token:
                        raise RuntimeError(
                            f"No refresh_token found in token file {token_data}."
                        )

                    data = {
                        "grant_type": "refresh_token",
                        "refresh_token": refresh_token,
                    }

                    response = requests.post(token_url, headers=headers, data=data)

                    if response.status_code == 200:
                        token_data_resp = response.json()
                        access_token = token_data_resp.get("access_token")
                        refresh_token_new = token_data_resp.get("refresh_token")
                        expires_in = token_data_resp.get("expires_in")

                        token_dict = {
                            "access_token": access_token,
                            "refresh_token": refresh_token_new,
                        }

                        if expires_in is not None:
                            try:
                                expires_in_int = int(expires_in)
                            except (TypeError, ValueError):
                                expires_in_int = None
                            if expires_in_int:
                                token_dict["expires_in"] = expires_in_int
                                token_dict["expires_at"] = (
                                    time.time() + expires_in_int - 60
                                )

                        json.write(token_dict, token_data)
                        return access_token

                    try:
                        err_body = response.json()
                    except ValueError:
                        err_body = {"raw": response.text}

                    if (
                        response.status_code == 400
                        and err_body.get("error") == "invalid_grant"
                        and "Token lineage has been revoked"
                        in err_body.get("error_description", "")
                    ):
                        raise RuntimeError(
                            "Canva refresh token has been revoked. "
                            "Delete your token file and re-run the OAuth flow "
                            "(canva.init(...)) to obtain new tokens."
                        )

                    if response.status_code == 429:
                        raise RuntimeError(
                            f"Failed to refresh token: 429, {err_body}. "
                            "Too many refresh_token requests. "
                            "Reduce concurrent refresh attempts and/or wait before retrying."
                        )

                    raise Exception(
                        f"Failed to refresh token: {response.status_code}, {err_body}"
                    )

            if token_data in Dict:
                refresh_token = token_data.get("refresh_token")
                if not refresh_token:
                    raise RuntimeError(
                        "No refresh_token found in in-memory token_data."
                    )

                data = {
                    "grant_type": "refresh_token",
                    "refresh_token": refresh_token,
                }

                response = requests.post(token_url, headers=headers, data=data)

                if response.status_code == 200:
                    token_data_resp = response.json()
                    access_token = token_data_resp.get("access_token")
                    refresh_token_new = token_data_resp.get("refresh_token")
                    expires_in = token_data_resp.get("expires_in")

                    token_data["access_token"] = access_token
                    token_data["refresh_token"] = refresh_token_new

                    if expires_in is not None:
                        try:
                            expires_in_int = int(expires_in)
                        except (TypeError, ValueError):
                            expires_in_int = None
                        if expires_in_int:
                            token_data["expires_in"] = expires_in_int
                            token_data["expires_at"] = (
                                time.time() + expires_in_int - 60
                            )

                    return access_token

                try:
                    err_body = response.json()
                except ValueError:
                    err_body = {"raw": response.text}

                if (
                    response.status_code == 400
                    and err_body.get("error") == "invalid_grant"
                    and "Token lineage has been revoked"
                    in err_body.get("error_description", "")
                ):
                    raise RuntimeError(
                        "Canva refresh token has been revoked. "
                        "Delete your token file and re-run the OAuth flow "
                        "(canva.init(...)) to obtain new tokens."
                    )

                if response.status_code == 429:
                    raise RuntimeError(
                        f"Failed to refresh token: 429, {err_body}. "
                        "Too many refresh_token requests. "
                        "Reduce concurrent refresh attempts and/or wait before retrying."
                    )

                raise Exception(
                    f"Failed to refresh token: {response.status_code}, {err_body}"
                )

            raise TypeError("token_data must be a File or Dict for refresh().")


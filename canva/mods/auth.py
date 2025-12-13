import os
import requests
import base64
import hashlib
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from typed import typed, Str, Nill, Dict, Path, Maybe, Union, File, Tuple
from utils import file, json, envs, cmd

def collect_after_sequence(input_string, sequence):
    index = input_string.find(sequence)
    if index != -1:
        return input_string[index + len(sequence):]
    else:
        return None

class auth:
    class scopes:
        @staticmethod
        def read():
            return 'app:read%20design:content:read%20design:meta:read%20design:permission:read%20folder:read%20folder:permission:read%20asset:read%20comment:read%20brandtemplate:meta:read%20brandtemplate:content:read%20profile:read'

        @staticmethod
        def write():
            return 'app:read%20app:write%20design:content:read%20design:meta:read%20design:content:write%20design:permission:read%20design:permission:write%20folder:read%20folder:write%20folder:permission:read%20folder:permission:write%20asset:read%20asset:write%20comment:read%20comment:write%20brandtemplate:meta:read%20brandtemplate:content:read%20profile:read'

    class code:
        @staticmethod
        def verifier():
            return base64.urlsafe_b64encode(os.urandom(32)).rstrip(b'=').decode('utf-8')

        @staticmethod
        def challenge(code_verifier):
            code_challenge = hashlib.sha256(code_verifier.encode()).digest()
            return base64.urlsafe_b64encode(code_challenge).rstrip(b'=').decode('utf-8')

    class token:
        class get:
            @typed
            def new(
                client_id: Maybe(Str)=None,
                client_secret: Maybe(Str)=None,
                scopes: Maybe(Str)=None,
                token_data: Union(Dict, Path)='canva.json'
            ) -> Maybe(Tuple):

                if not client_id:
                    client_id = envs.get('CANVA_CLIENT_ID')
                    if not client_id:
                        raise ValueError("Client ID not provided.")

                if not client_secret:
                    client_secret = envs.get('CANVA_CLIENT_SECRET')
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
                        access_token = token_data_.get('access_token')
                        refresh_token = token_data_.get('refresh_token')
                    except:
                        pass

                if token_data in Dict:
                    access_token = token_data.get('access_token')
                    refresh_token = token_data.get('refresh_token')

                if access_token and refresh_token:
                    return access_token, refresh_token

                code_verifier = auth.code.verifier()
                code_challenge = auth.code.challenge(code_verifier)

                redirect_uri = 'http://127.0.0.1:8080'
                authorization_url = (
                    f"https://www.canva.com/api/oauth/authorize?"
                    f"response_type=code&client_id={client_id}&redirect_uri={redirect_uri}&scope={scopes}&code_challenge={code_challenge}&code_challenge_method=S256"
                )

                webbrowser.open(authorization_url)

                class OAuthHandler(BaseHTTPRequestHandler):
                    def do_GET(self):
                        query = urlparse(self.path).query
                        params = parse_qs(query)
                        auth_code = params.get('code', [None])[0]

                        self.send_response(200)
                        self.send_header('Content-type', 'text/html')
                        self.end_headers()
                        self.wfile.write(b'Thank you! You have authorized the app. You can now close this window.')

                        self.server.auth_code = auth_code

                with HTTPServer(('127.0.0.1', 8080), OAuthHandler) as httpd:
                    print('Listening for authorization code...')
                    httpd.handle_request()

                auth_code = getattr(httpd, 'auth_code', None)
                if not auth_code:
                    raise ValueError("Failed to obtain authorization code.")


                token_url = 'https://api.canva.com/rest/v1/oauth/token'
                credentials = f"{client_id}:{client_secret}"
                encoded_credentials = base64.b64encode(credentials.encode()).decode()

                headers = {
                    'Authorization': f'Basic {encoded_credentials}',
                    'Content-Type': 'application/x-www-form-urlencoded',
                }

                data = {
                    'grant_type': 'authorization_code',
                    'code': auth_code,
                    'redirect_uri': 'http://127.0.0.1:8080',
                    'code_verifier': code_verifier,
                }

                response = requests.post(token_url, headers=headers, data=data)

                if response.status_code == 200:
                    token_data_ = response.json()
                    access_token = token_data_.get('access_token')
                    refresh_token = token_data_.get('refresh_token')

                    token_dict = {
                        'access_token': access_token,
                        'refresh_token': refresh_token
                    }

                    if token_data in Path:
                        json.write(token_dict, token_data)

                    print('Tokens saved to tokens.json')
                else:
                    print('Error:', response.status_code)
                    print('Response:', response.text)

            @typed
            def current(token_data: Union(File, Dict)) -> Str:
                if token_data in File:
                    data = json.read(token_data)
                    current_token = data.get('access_token')
                    if current_token:
                        return current_token
                    raise ValueError(f'There is no access token defined in {token_data}.')

                if token_data in Dict:
                    current_token = token_data.get('access_token')
                    if current_token:
                        return current_token
                    raise ValueError(f'There is no access token defined in {token_data}.')

        @typed
        def refresh(client_id: Maybe(Str)=None, client_secret: Maybe(Str)=None, token_data: Union(File, Dict)='canva.json') -> Str:
            token_url = 'https://api.canva.com/rest/v1/oauth/token'
            credentials = f"{client_id}:{client_secret}"
            encoded_credentials = base64.b64encode(credentials.encode()).decode()

            headers = {
                'Authorization': f'Basic {encoded_credentials}',
                'Content-Type': 'application/x-www-form-urlencoded',
            }

            if token_data in File:
                token_data_ = json.read(token_data)
                refresh_token = token_data_.get('refresh_token')
            if token_data in Dict:
                refresh_token = token_data.get('refresh_token')

            data = {
                'grant_type': 'refresh_token',
                'refresh_token': refresh_token,
            }

            response = requests.post(token_url, headers=headers, data=data)

            if response.status_code == 200:
                token_data_resp = response.json()
                access_token = token_data_resp.get('access_token')
                refresh_token = token_data_resp.get('refresh_token')

                token_dict = {
                    'access_token': access_token,
                    'refresh_token': refresh_token
                }

                if token_data in File:
                    json.write(token_dict, token_data)

                return access_token

            try:
                err_body = response.json()
            except ValueError:
                err_body = {"raw": response.text}

            if (
                response.status_code == 400
                and err_body.get("error") == "invalid_grant"
                and "Token lineage has been revoked" in err_body.get("error_description", "")
            ):
                raise RuntimeError(
                    "Canva refresh token has been revoked. "
                    "Delete your token file and re-run the OAuth flow "
                    "(canva.init(...)) to obtain new tokens."
                )

            if response.status_code == 429:
                raise RuntimeError(
                    f"Canva refresh token rate-limited (429): {err_body}. "
                    "Reduce concurrent refresh attempts and/or wait before retrying."
                )

            raise Exception(
                f"Failed to refresh token: {response.status_code}, {err_body}"
            )


            raise Exception(
                f"Failed to refresh token: {response.status_code}, {err_body}"
            )


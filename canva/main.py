from canva.mods.auth   import auth
from canva.mods.folder import folder
from canva.mods.design import design
from canva.mods.page   import page
from canva.mods.export import export
import os
import json

class Canva:
    auth   = auth
    folder = folder
    design = design
    page   = page
    export = export

    def init(client_id=None, client_secret=None, token_file="canva.json"):
        if not os.path.exists(token_file):
            Canva.auth.token.get.new(client_id, client_secret, Canva.auth.scopes.write(), token_file)

        with open(token_file, 'r') as tf:
            token_data = json.load(tf)
            access_token = token_data.get('access_token', '')
            if not access_token:
                Canva.auth.token.get.new(client_id, client_secret, Canva.auth.scopes.write(), token_file)



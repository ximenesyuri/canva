from typed import typed, Maybe, Str, Path, Dict, Nill
from canva.mods.auth   import auth
from canva.mods.folder import folder
from canva.mods.design import design
from canva.mods.page   import page
from canva.mods.export import export

class Canva:
    auth   = auth
    folder = folder
    design = design
    page   = page
    export = export

    @typed
    def init(client_id: Maybe(Str)=None, client_secret: Maybe(Str)=None, scopes: Maybe(Str)=None, token_file: Path="canva.json") -> Nill:
        Canva.auth.token.get.new(
            client_id=client_id,
            client_secret=client_secret,
            scopes=scopes,
            token_data=token_file
        )

Canva.init()

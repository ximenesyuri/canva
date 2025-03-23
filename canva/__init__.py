from canva.main import Canva
from pathlib import Path
import os
import json
from dotenv import load_dotenv

canva = Canva
cv    = canva

MAIN_DIR = Path(os.path.dirname(__file__), '..').resolve()
token_file = os.path.join(MAIN_DIR, 'canva.json')
load_dotenv(os.path.join(MAIN_DIR, '.env'))

client_id = os.getenv('CANVA_CLIENT_ID')
client_secret = os.getenv('CANVA_CLIENT_SECRET')

if not os.path.exists(token_file):
    cv.auth.token.get(client_id, client_secret, cv.auth.scopes.write(), token_file)

with open(token_file, 'r') as tf:
    token_data = json.load(tf)
    access_token = token_data.get('access_token', '')
    if not access_token:
        cv.auth.token.get(client_id, client_secret, cv.auth.scopes.write(), token_file)

print(cv.design.list(client_id, client_secret, token_file))

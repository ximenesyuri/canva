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

canva.init(client_id, client_secret, token_file)

design_id = cv.design.get.id('vórtice', client_id, client_secret, token_file)
export_id = cv.export.design.png(design_id, True, client_id, client_secret, token_file)

while True:
    export_status = cv.export.get.status(export_id, client_id, client_secret, token_file)
    if export_status == 'success':
        url = cv.export.get.url(export_id, client_id, client_secret, token_file)
        break

print(url)


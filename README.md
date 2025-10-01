# About

`canva` is an intuitive Python client for the core functionalities of [canva.com](https://canva.com) API.

# Install

With `pip`:
```bash
pip install git+https://github.com/pythonalta/canva
```

With [py](https://github.com/ximenesyuri/py):
```bash
py install ximenesyuri/canva
```

# Authentication

1. Create an integration in [canva.com/developers](https://www.canva.com/developers/integrations/connect-api)
2. Follow the instructions to get a `client_id` and a `client_secret`.

```
from canva import canva

canva.init(
    client_id='your client ID',
    client_secret='your client secret',
    token_file='where/to/save/your/tokens.json'
)
```

# Usage

```
canva.design.list(client_id, client_secret, token_file)
...
```

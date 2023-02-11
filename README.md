# Overall
Rest API client for Python

Simple REST API client for Python

## Installation

Use the package manager pip to install our client in Python.

```bash
pip install gawsoft-api-client
```

OR
```bash
pip3 install gawsoft-api-client
```

## Usage

### Take screenshot and save jpg to file
```python
from gawsoft.api_client import Request, Response

class Client(Request):
    def __init__(self, api_key, api_version='v1', api_host ='http://api.example.com', user_agent='Example Api Python client'):
        super.__init__(api_key, api_version, api_host, user_agent)
    
    def info(self, link: str, params: dict) -> Response:
        return self.request('/info', 'POST', params)
```

## License
[MIT](https://choosealicense.com/licenses/mit/)
# Overall

Generic REST API client for Python

## Installation

Initially this library is available only on github, however I plan to publish on
pypi.org when it becomes stable.


```sh
pipx install git+https://github.com/wtfo-guru/rest-api-client-framework.git
```


## Usage

Write your client api

```python

from api_client.endpoint import Endpoint
from api_client.request import RestRequest
from api_client.response import RestResponse


endpoint = Endpoint(
    name="disable_blocking",
    path="/api/settings/temporaryDisableBlocking",
    request_method=HTTPMethod.GET,
    query_parameters=("minutes"),
)
req = RestRequest(
    endpoints=endpoint,
    api_root="https://technitium.examplse.com,
    user_agent="I am an example client",
)

resp = req.call_endpoint("disable_blocking", token="apitoken", minutes=5)
```


## Tests

```sh

make test
```

## License

[MIT](https://choosealicense.com/licenses/mit/)

## Credits

This project is based upon source from:

[gawsoftpl/rest-api-client-framework-python](https://github.com/gawsoftpl/rest-api-client-framework-python)

[paolorechia/rest-api-client](https://github.com/paolorechia/rest-api-client)

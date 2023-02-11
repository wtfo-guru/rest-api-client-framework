from gawsoft.api_client import Request, Response


class Client(Request):
    def __init__(
        self,
        api_key: str,
        api_version: str ='v1',
        api_host: str = 'http://api.example.com',
        user_agent: str = 'Example Api Python client'
     ):
        super.__init__(api_key, api_version, api_host, user_agent)

    def info(self, link: str, params: dict) -> Response:
        return self.request('/info', 'POST', params)
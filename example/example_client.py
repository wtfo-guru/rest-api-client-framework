from gawsoft.api_client import Request, Response


class Client(Request):
    def __init__(
        self,
        api_key: str,
        api_version: str ='',
        api_host: str = 'http://httpbin.org',
        user_agent: str = 'Example Api Python client'
     ):
        super().__init__(api_key, api_version, api_host, user_agent)

    def info(self, link: str, params: dict = {}) -> Response:
        return self.request(link, 'POST', params)


c = Client("abc")
response = c.info("delay/1")
print(response.status_code)
print(response.data())
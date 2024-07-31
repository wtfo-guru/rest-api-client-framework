from pydantic import BaseModel, HttpUrl

class Wtf(BaseModel):

    api_root: HttpUrl


rack = Wtf(api_root="https://pridns-proxy.metaorg.com")

print(rack.api_root)
print(repr(rack.api_root))
print(str(rack.api_root))

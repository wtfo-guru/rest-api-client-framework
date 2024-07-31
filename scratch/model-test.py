from datetime import datetime
from pydantic import BaseModel

class MyModel(BaseModel):
    year: int
    month: str
    active: bool
    when: datetime


m = MyModel(year=1972, month="February", active=True, when=datetime.now())

print(m.model_dump())

print(m.model_dump_json())

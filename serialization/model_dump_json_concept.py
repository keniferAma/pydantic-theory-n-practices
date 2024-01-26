#### model_dump_json ####

from datetime import datetime

from pydantic import BaseModel


class BarModel(BaseModel):
    whatever: int


class FooBarModel(BaseModel):
    foo: datetime
    bar: BarModel


m = FooBarModel(foo=datetime(2032, 6, 1, 12, 13, 14), bar={'whatever': 123})
print(m.model_dump_json())
#> {"foo":"2032-06-01T12:13:14","bar":{"whatever":123}}
print(m.model_dump_json(indent=4))
"""
{
  "foo": "2032-06-01T12:13:14",
  "bar": {
    "whatever": 123
  }
}
"""

# We can confuse this model with model_dump, but they're different. model_dump gives us a dictionary which could
# be easier to work with in the program, while model_dump_json is strictly speaking a json format with its 
# features. So with this mode we'll be able to treat it as a json data.
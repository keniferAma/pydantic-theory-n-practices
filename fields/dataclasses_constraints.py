"""init_var: Whether the field should be seen as an init-only field in the dataclass.
kw_only: Whether the field should be a keyword-only argument in the constructor of the dataclass."""

from pydantic import BaseModel, Field
from pydantic.dataclasses import dataclass


@dataclass
class Foo:
    bar: str
    baz: str = Field(init_var=True)
    qux: str = Field(kw_only=True)


class Model(BaseModel):
    foo: Foo


model = Model(foo=Foo('bar', baz='baz', qux='qux'))
print(model.model_dump())  
#> {'foo': {'bar': 'bar', 'qux': 'qux'}}

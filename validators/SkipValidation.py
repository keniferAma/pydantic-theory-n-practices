# some SkipValidation concepts #

from typing import List

from pydantic import BaseModel, SkipValidation


class Model(BaseModel):
    names: List[SkipValidation[str]]


m = Model(names=['foo', 'bar'])
print(m)
#> names=['foo', 'bar']

m = Model(names=['foo', 123])  
print(m)
#> names=['foo', 123]

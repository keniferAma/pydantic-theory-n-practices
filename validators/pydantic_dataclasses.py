from pydantic import field_validator
from pydantic.dataclasses import dataclass


@dataclass
class DemoDataclass:
    product_id: str  # should be a five-digit string, may have leading zeros.
    # As we know without basemodel we can't parse the type at the beginning. so withc only dataclass we can not parse 
    # the atributes types.
    @field_validator('product_id', mode='before')
    @classmethod
    def convert_int_serial(cls, v):
        if isinstance(v, int):
            v = str(v).zfill(5)
        return v


print(DemoDataclass(product_id='01234'))
#> DemoDataclass(product_id='01234')
print(DemoDataclass(product_id=2468))
#> DemoDataclass(product_id='02468')
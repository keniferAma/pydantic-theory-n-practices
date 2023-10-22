                                    ## Annotated validators ##

from typing import Any, List

from typing_extensions import Annotated

from pydantic import BaseModel, ValidationError
from pydantic.functional_validators import AfterValidator


def check_squares(v: int) -> int:
    assert v**0.5 % 1 == 0, f'{v} is not a square number'
    return v


def double(v: Any) -> Any:
    return v * 2


MyNumber = Annotated[int, AfterValidator(double), AfterValidator(check_squares)]
# AfterValitator only is used with Annotated.
# After pydantic through basemodel verifies the field (in this specific case "int"), then goes to validate
# "AfterValidator" and what it is inside, on this case the functions we set earlier.



class DemoModel(BaseModel):
    number: List[MyNumber] # We set the annotated as int, so first basemodel will verify if that matches, then
    # goes to verify AfterValitator.
    # We can give the AfterValitator functions as list, as we set in the field.


print(DemoModel(number=[2, 8]))
#> number=[4, 16]
try:
    DemoModel(number=[2, 4])
except ValidationError as e:
    print(e)
    """
    1 validation error for DemoModel
    number.1
      Assertion failed, 8 is not a square number
    assert ((8 ** 0.5) % 1) == 0 [type=assertion_error, input_value=4, input_type=int]
    """



########## @field_validator @model_validator ##########
# Al parecer la principal diferencia radica en que en @field_validator debemos especificar que fields o campos
# vamos a analizar, mientras que con @model_validator es de manera mas global.

from typing_extensions import Annotated

from pydantic import BaseModel, Field, field_validator


class Model(BaseModel):
    x: str = 'abc'
    y: Annotated[str, Field(validate_default=True)] = 'xyz'

    @field_validator('x', 'y')
    @classmethod
    def double(cls, v: str) -> str:
        return v * 2


print(Model())
#> x='abc' y='xyzxyz'
print(Model(x='foo'))
#> x='foofoo' y='xyzxyz'
print(Model(x='abc'))
#> x='abcabc' y='xyzxyz'
print(Model(x='foo', y='bar'))
#> x='foofoo' y='barbar





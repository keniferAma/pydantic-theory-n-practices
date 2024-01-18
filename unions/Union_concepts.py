# Unions annotates needs ONLY one member to be VALID.


"""
SOME CONSIDERATIONS:

*left to right mode - the simplest approach, each member of the union is tried in order and 
the first match is returned
*smart mode - similar to "left to right mode" members are tried in order; 
however, validation will proceed past the first match to attempt to find a better match, 
this is the default mode for most union validation
*discriminated unions - only one member of the union is tried, based on a discriminator"""


# left_to_right mode #

from typing import Union

from pydantic import BaseModel, Field, ValidationError


class User(BaseModel):
    id: Union[str, int] = Field(union_mode='left_to_right')


print(User(id=123))
#> id=123
print(User(id='hello'))
#> id='hello'

try:
    User(id=[])
except ValidationError as e:
    print(e)
    """
    2 validation errors for User
    id.str
      Input should be a valid string [type=string_type, input_value=[], input_type=list]
    id.int
      Input should be a valid integer [type=int_type, input_value=[], input_type=list]
    """


# Union is set 'smart' as default. # 
    


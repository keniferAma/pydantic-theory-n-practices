
import json
from enum import Enum
from typing import Union

from typing_extensions import Annotated

from pydantic import BaseModel, Field
from pydantic.config import ConfigDict


class FooBar(BaseModel):
    count: int
    size: Union[float, None] = None


class Gender(str, Enum):
    male = 'male'
    female = 'female'
    other = 'other'
    not_given = 'not_given'

class MainModel(BaseModel):
    """
    This is the description of the main model
    """

    model_config = ConfigDict(title='Main')

    foo_bar: FooBar
    gender: Annotated[Union[Gender, None], Field(alias='Gender')] = None
    snap: int = Field(
        42,
        title='The Snap',
        description='this is the value of snap',
        gt=30,
        lt=50,
    )


print(json.dumps(MainModel.model_json_schema(), indent=2))
# To remember: json.dumps() prints in json format, but be carefull adding model_json_schema, which gives us
# the object in json format.
# json.dumps() is escential if we want to serialize python objects into json format. REMEMBER: It is not the same
# to generate a model_json_schema instead of using json.dump(), with the first one we're showing a python object
# while with the second one we'er serializating.
# ALSO REMEMBER: json.dump() is used to serialize objects into json format.(the regular way) and json.dumps()
# is used to print() in the json format.






#### TypeAdapter schema ####
from typing import List

from pydantic import TypeAdapter

adapter = TypeAdapter(List[int])
print(adapter.json_schema())
#> {'items': {'type': 'integer'}, 'type': 'array'}




#### Json serialization with model_config (some commands)#####
"""
*title
*use_enum_values
*json_schema_extra
*ser_json_timedelta
*ser_json_bytes
*ser_json_inf_nan"""

# It seems ConfigDict() accepts all these keywords without helping us with the automatic generative responses.
# But remember the structure: model_config = ConfigDict()



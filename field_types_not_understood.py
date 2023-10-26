# On this module we're gonna store all the information we don't know yet.




                                        ####### __pydantic_config__ ########







# from typing import Optional

# from typing_extensions import TypedDict

# from pydantic import ConfigDict, TypeAdapter, ValidationError


# # `total=False` means keys are non-required
# class UserIdentity(TypedDict, total=False):
#     name: Optional[str]
#     surname: str


# class User(TypedDict):
#     __pydantic_config__ = ConfigDict(extra='forbid')

#     identity: UserIdentity
#     age: int


# ta = TypeAdapter(User)

# print(
#     ta.validate_python(
#         {'identity': {'name': 'Smith', 'surname': 'John'}, 'age': 37}
#     )
# )
# #> {'identity': {'name': 'Smith', 'surname': 'John'}, 'age': 37}

# print(
#     ta.validate_python(
#         {'identity': {'name': None, 'surname': 'John'}, 'age': 37}
#     )
# )
# #> {'identity': {'name': None, 'surname': 'John'}, 'age': 37}

# print(ta.validate_python({'identity': {}, 'age': 37}))
# #> {'identity': {}, 'age': 37}


# try:
#     ta.validate_python(
#         {'identity': {'name': ['Smith'], 'surname': 'John'}, 'age': 24}
#     )
# except ValidationError as e:
#     print(e)
#     """
#     1 validation error for typed-dict
#     identity.name
#       Input should be a valid string [type=string_type, input_value=['Smith'], input_type=list]
#     """

# try:
#     ta.validate_python(
#         {
#             'identity': {'name': 'Smith', 'surname': 'John'},
#             'age': '37',
#             'email': 'john.smith@me.com',
#         }
#     )
# except ValidationError as e:
#     print(e)
#     """
#     1 validation error for typed-dict
#     email
#       Extra inputs are not permitted [type=extra_forbidden, input_value='john.smith@me.com', input_type=str]
#     """




from typing import Optional

from typing_extensions import Annotated

from pydantic import (
    BaseModel,
    EncodedBytes,
    EncodedStr,
    EncoderProtocol,
    ValidationError,
)


class MyEncoder(EncoderProtocol):
    @classmethod
    def decode(cls, data: bytes) -> bytes:
        if data == b'**undecodable**':
            raise ValueError('Cannot decode data')
        return data[13:]

    @classmethod
    def encode(cls, value: bytes) -> bytes:
        return b'**encoded**: ' + value

    @classmethod
    def get_json_format(cls) -> str:
        return 'my-encoder'


MyEncodedBytes = Annotated[bytes, EncodedBytes(encoder=MyEncoder)]
MyEncodedStr = Annotated[str, EncodedStr(encoder=MyEncoder)]


class Model(BaseModel):
    my_encoded_bytes: MyEncodedBytes
    my_encoded_str: Optional[MyEncodedStr] = None


# Initialize the model with encoded data
m = Model(
    my_encoded_bytes=b'**encoded**: some bytes',
    my_encoded_str='**encoded**: some str',
)

# Access decoded value
print(m.my_encoded_bytes)
#> b'some bytes'
print(m.my_encoded_str)
#> some str

# Serialize into the encoded form
print(m.model_dump())
"""
{
    'my_encoded_bytes': b'**encoded**: some bytes',
    'my_encoded_str': '**encoded**: some str',
}
"""

# Validate encoded data
try:
    Model(my_encoded_bytes=b'**undecodable**')
except ValidationError as e:
    print(e)
    """
    1 validation error for Model
    my_encoded_bytes
      Value error, Cannot decode data [type=value_error, input_value=b'**undecodable**', input_type=bytes]
    """



## encode and decode applied to pydantic.



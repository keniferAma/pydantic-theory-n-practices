                                            ##### Literal #####
# As we already knew, we only have the options inside the brackets.
from typing import Literal

from pydantic import BaseModel, ValidationError


class Pie(BaseModel):
    flavor: Literal['apple', 'pumpkin']


Pie(flavor='apple')
Pie(flavor='pumpkin')
try:
    Pie(flavor='cherry')
except ValidationError as e:
    print(str(e))
    """
    1 validation error for Pie
    flavor
      Input should be 'apple' or 'pumpkin' [type=literal_error, input_value='cherry', input_type=str]
    """



### info about union:
# we can use union[] to set a field that acepts more types, for example:
# we can set union[List, Dict] for a field that can accept lists and dicts.


from typing import ClassVar, List, Literal, Union

from pydantic import BaseModel, ValidationError


class Cake(BaseModel):
    kind: Literal['cake']
    required_utensils: ClassVar[List[str]] = ['fork', 'knife']
    # To remember, this ClassVar it's like:
    # the class variable that is not exposed directly to the instance, to the "self" in traditional class.
    # It's a variable inside the class.


class IceCream(BaseModel):
    kind: Literal['icecream']
    required_utensils: ClassVar[List[str]] = ['spoon']
    


class Meal(BaseModel):
    dessert: Union[Cake, IceCream]


print(type(Meal(dessert={'kind': 'cake'}).dessert).__name__)
#> Cake
print(type(Meal(dessert={'kind': 'icecream'}).dessert).__name__)
#> IceCream
try:
    Meal(dessert={'kind': 'pie'})
except ValidationError as e:
    print(str(e))
    """
    2 validation errors for Meal
    dessert.Cake.kind
      Input should be 'cake' [type=literal_error, input_value='pie', input_type=str]
    dessert.IceCream.kind
      Input should be 'icecream' [type=literal_error, input_value='pie', input_type=str]
    """



"""With proper ordering in an annotated Union, you can use this to parse types of decreasing specificity:"""

from typing import Literal, Optional, Union

from pydantic import BaseModel


class Dessert(BaseModel):
    kind: str


class Pie(Dessert):
    kind: Literal['pie']
    flavor: Optional[str]


class ApplePie(Pie):
    flavor: Literal['apple']


class PumpkinPie(Pie):
    flavor: Literal['pumpkin']


class Meal(BaseModel):
    dessert: Union[ApplePie, PumpkinPie, Pie, Dessert]


print(type(Meal(dessert={'kind': 'pie', 'flavor': 'apple'}).dessert).__name__)
#> ApplePie
print(type(Meal(dessert={'kind': 'pie', 'flavor': 'pumpkin'}).dessert).__name__)
#> PumpkinPie
print(type(Meal(dessert={'kind': 'pie'}).dessert).__name__)
#> Dessert
print(type(Meal(dessert={'kind': 'cake'}).dessert).__name__)
#> Dessert
print(type(Meal(dessert={'kind': 'pie', 'flavor': 'strawberry'}).dessert).__name__) # This one we set it up.
# Pie








                                         ### Booleans ###
"""A standard bool field will raise a ValidationError if the value is not one of the following:

A valid boolean (i.e. True or False),
The integers 0 or 1,
a str which when converted to lower case is one of '0', 'off', 'f', 'false', 'n', 'no', '1', 'on', 't', 'true', 'y', 'yes'
a bytes which is valid per the previous rule when decoded to str"""

from pydantic import BaseModel, ValidationError


class BooleanModel(BaseModel):
    bool_value: bool


print(BooleanModel(bool_value=False))
#> bool_value=False
print(BooleanModel(bool_value='False'))
#> bool_value=False
print(BooleanModel(bool_value=1))
#> bool_value=True
try:
    BooleanModel(bool_value=[])
except ValidationError as e:
    print(str(e))
    """
    1 validation error for BooleanModel
    bool_value
      Input should be a valid boolean [type=bool_type, input_value=[], input_type=list]
    """         






                                                ### TypedDict ###    
"""A TypedDict is a special type of dictionary in Python that allows you to specify the types of the values 
based on their keys. This means that you can define a dictionary where each key is associated with a specific type, 
and the values for that key must be of that type.

For example, let’s say you have a dictionary representing a person, with keys for their name and age. 
You could define a TypedDict like this:"""

from typing_extensions import TypedDict

class Person(TypedDict):
    name: str
    age: int

"""This TypedDict specifies that the name key must have a value of type str, and the age key must 
have a value of type int. If you try to create a dictionary using this TypedDict with values of the wrong type, 
you will get an error."""                                                
                                                
                                               
"""TypedDict declares a dictionary type that expects all of its instances to have a certain set of keys, 
where each key is associated with a value of a consistent type.

It is same as dict but Pydantic will validate the dictionary since keys are annotated."""                                                        


from typing_extensions import TypedDict

from pydantic import TypeAdapter, ValidationError


class User(TypedDict):
    name: str
    id: int


ta = TypeAdapter(User) # this works like a validator, it's like a kind of "basemodel" but applied to 
# objects like this one (TypeDict).
# "validate_python" is a method inside of TypeAdapter that executes the example.
"""The TypeAdapter class from the pydantic library can be used as a validator for data types 
that do not have built-in validation methods"""

print(ta.validate_python({'name': 'foo', 'id': 1}))
#> {'name': 'foo', 'id': 1}


try:
    ta.validate_python({'name': 'foo'})
except ValidationError as e:
    print(e)
    """
    1 validation error for typed-dict
    id
      Field required [type=missing, input_value={'name': 'foo'}, input_type=dict]
    """








                                        #### Encode - decode bytes ####
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
        if data == b'**undecodable**': # "b" means byte.
            raise ValueError('Cannot decode data')
        return data[13:]

    @classmethod
    def encode(cls, value: bytes) -> bytes:
        return b'**encoded**: ' + value

    @classmethod
    def get_json_format(cls) -> str:
        return 'my-encoder'


MyEncodedBytes = Annotated[bytes, EncodedBytes(encoder=MyEncoder)]
MyEncodedStr = Annotated[str, EncodedStr(encoder=MyEncoder)] ## THE SECOND ELEMENT IS THE METADATA.
# Remember that "Annotated" is used to add metadata (from the second element) to the value, 


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








                                ## base64 applied to pydantic ##


from typing import Optional

from pydantic import Base64Bytes, Base64Str, BaseModel, ValidationError


class Model(BaseModel):
    base64_bytes: Base64Bytes
    base64_str: Optional[Base64Str] = None


# Initialize the model with base64 data
m = Model(
    base64_bytes=b'VGhpcyBpcyB0aGUgd2F5',
    base64_str='VGhlc2UgYXJlbid0IHRoZSBkcm9pZHMgeW91J3JlIGxvb2tpbmcgZm9y',
)

# Access decoded value
print(m.base64_bytes)
#> b'This is the way'
print(m.base64_str)
#> These aren't the droids you're looking for

# Serialize into the base64 form
print(m.model_dump())
"""
{
    'base64_bytes': b'VGhpcyBpcyB0aGUgd2F5\n',
    'base64_str': 'VGhlc2UgYXJlbid0IHRoZSBkcm9pZHMgeW91J3JlIGxvb2tpbmcgZm9y\n',
}
"""

# Validate base64 data
try:
    print(Model(base64_bytes=b'undecodable').base64_bytes)
except ValidationError as e:
    print(e)
    """
    1 validation error for Model
    base64_bytes
      Base64 decoding error: 'Incorrect padding' [type=base64_decode, input_value=b'undecodable', input_type=bytes]
    """







                                        ## more Annotated (METADATA) ##
from typing_extensions import Annotated

from pydantic import (
    AfterValidator,
    PlainSerializer,
    TypeAdapter,
    WithJsonSchema,
)

TruncatedFloat = Annotated[
    float,
    AfterValidator(lambda x: round(x, 1)),
    PlainSerializer(lambda x: f'{x:.1e}', return_type=str),
    WithJsonSchema({'type': 'string'}, mode='serialization'),
]


ta = TypeAdapter(TruncatedFloat)

input = 1.02345
assert input != 1.0

assert ta.validate_python(input) == 1.0

assert ta.dump_json(input) == b'"1.0e+00"'

assert ta.json_schema(mode='validation') == {'type': 'number'}
assert ta.json_schema(mode='serialization') == {'type': 'string'}

"""En el contexto de la programación y en este caso específico de Pydantic, los metadatos se utilizan para 
proporcionar información adicional o instrucciones sobre cómo se debe manejar un tipo de datos específico.

En el ejemplo que proporcionaste, TruncatedFloat es un tipo de datos personalizado que está anotado con ciertos 
metadatos. Estos metadatos no son valores en sí mismos, sino más bien instrucciones sobre cómo se debe manejar un 
valor de tipo TruncatedFloat.

AfterValidator(lambda x: round(x, 1)) es una instrucción que dice “después de validar este dato, redóndalo a un 
decimal”.
PlainSerializer(lambda x: f'{x:.1e}', return_type=str) es una instrucción que dice “cuando serialices este 
dato a una cadena, formátalo en notación científica con un decimal”.
WithJsonSchema({'type': 'string'}, mode='serialization') es una instrucción que dice “cuando generes un 
esquema JSON para este dato en modo de serialización, el tipo debe ser una cadena”.
Por lo tanto, aunque estos metadatos pueden parecer valores a primera vista, en realidad son instrucciones 
codificadas que modifican el comportamiento del tipo de datos anotado. Espero que esto aclare tu confusión. 
"""



# Sequence and TypeVar:

from typing import Any, List, Sequence, TypeVar

from annotated_types import Gt, Len
from typing_extensions import Annotated

from pydantic import ValidationError
from pydantic.type_adapter import TypeAdapter

SequenceType = TypeVar('SequenceType', bound=Sequence[Any]) # With Sequence we MUST give a secuence of any on this 
# case, but it also must be a secuence like a list or a tuple. 

# We are using TypeVar as argument in Annotated instead of an inheritated class.
# And we're also using Len to set a constriction in the list length.
ShortSequence = Annotated[SequenceType, Len(max_length=10)]


ta = TypeAdapter(ShortSequence[List[int]])

v = ta.validate_python([1, 2, 3, 4, 5])
assert v == [1, 2, 3, 4, 5]

try:
    ta.validate_python([1] * 100)
except ValidationError as exc:
    print(exc)
    """
    1 validation error for list[int]
      List should have at most 10 items after validation, not 11 [type=too_long, input_value=[1, 1, 1, 1, 1, 1, 1, 1, ... 1, 1, 1, 1, 1, 1, 1, 1], input_type=list]
    """


T = TypeVar('T')  # or a bound=SupportGt

PositiveList = List[Annotated[T, Gt(0)]]

ta = TypeAdapter(PositiveList[float])

v = ta.validate_python([1])
assert type(v[0]) is float


try:
    ta.validate_python([-1])
except ValidationError as exc:
    print(exc)
    """
    1 validation error for list[constrained-float]
    0
      Input should be greater than 0 [type=greater_than, input_value=-1, input_type=int]
    """
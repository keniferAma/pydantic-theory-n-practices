

                                         ## exercising "union" ##

from pydantic import BaseModel
from typing import Union, List, Dict



class Union(BaseModel):
    name: str
    age: int
    hobbies: Union[List[str], Dict]

j = Union(name='abelardo', age=23, hobbies=['play videogames', 'taking the sun'])
print(j.model_dump())
"""{'name': 'abelardo', 'age': 23, 'hobbies': ['play videogames', 'taking the sun']}"""

g = Union(name='abelardo', age=23, hobbies={'juegos': 'consolas', 'taking': 'sun'})
print(g.model_dump())
"""{'name': 'abelardo', 'age': 23, 'hobbies': {'juegos': 'consolas', 'taking': 'sun'}}"""



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





#Excercising TypeDict and TypeAdapter:

from typing_extensions import TypedDict
from pydantic import TypeAdapter


class Typing_without_keys(TypedDict):
    name: str
    age: int

ta = TypeAdapter(Typing_without_keys)

print(ta.validate_python({'name': 'carlos', 'age': '2'}))








### understanding more about TypeAdapter ###


from typing_extensions import Annotated
from pydantic import Field, TypeAdapter, ValidationError

# Define a custom type using pydantic
PositiveInt = Annotated[int, Field(gt=False)] # setting a constriction with Field.(gt=greater than)
ta = TypeAdapter(PositiveInt)

# Validate a value using TypeAdapter
try:
    ta.validate_python(-1)
except ValidationError as exc:
    print(f"TypeAdapter validation error: {exc}")

# Validate a value using assert
try:
    x = -1
    assert x > 0, f"Value must be greater than 0, but got {x}"
except AssertionError as exc:
    print(f"Assertion error: {exc}")








## some practices with TypeAdapter ##

from pydantic import TypeAdapter, PrivateAttr, ConfigDict, SerializeAsAny
from typing_extensions import TypedDict



class Type(TypedDict):
    names: List[str]
    dates: Dict[str, int]

# Remember instancing TypeDict
ta = TypeAdapter(Type)

values = Type(names=["alejandro", "albeiro"], dates={"casa": "12"})
"""{'names': ['alejandro', 'albeiro'], 'dates': {'casa': 12}}"""
# To remember: TypeAdapter works as a kind of validator, we're not inheritating from basemodel so, this is
# a recursive way to solve it.

print(ta.validate_python(values))





# Some rememberings about Field, model_config, PrivateAttr
class Repase(BaseModel):
    model_config = ConfigDict(frozen="y", extra="allow") # Remember to set extra to allow __pydantic_extra__.

    name: str = Field(default="marlon")
    surname: str = Field(alias="apellido")
    city: str = Field(exclude=True)
    _age: int = PrivateAttr(default=30)


re = Repase(apellido="jimenez", city="orlando", extra="fall")

print(re.model_dump())
print(re.__pydantic_extra__)


try: 
    re.city = "madrid"

except ValidationError as e:
    print(e)
"""Instance is frozen [type=frozen_instance, input_value='madrid', input_type=str]
    For further information visit https://errors.pydantic.dev/2.1/v/frozen_instance"""







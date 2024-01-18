from pydantic import ConfigDict, Field, BaseModel, ValidationError


class NoExtraArguments(BaseModel):
    model_config = ConfigDict(str_max_length=5) # This applies for the entire model.
    name: str
    surname: str
    age: int


try:
    object_1 = NoExtraArguments(name='Miguel', surname='Cardona', age=12)

except ValidationError as m:
    print(m)
"""2 validation errors for NoExtraArguments
name
  String should have at most 5 characters [type=string_too_long, input_value='Miguel', input_type=str]       
    For further information visit https://errors.pydantic.dev/2.5/v/string_too_long
surname
  String should have at most 5 characters [type=string_too_long, input_value='Cardona', input_type=str]      
    For further information visit https://errors.pydantic.dev/2.5/v/string_too_long"""



### dataclasses ConfigDict ###

from pydantic.dataclasses import dataclass


model_config_for_dataclasse = ConfigDict(str_max_length=5)


@dataclass(config=model_config_for_dataclasse)
class MyPydanticDataClass:
    name: str
    surname: str
    age: int

try:
    object_2 = MyPydanticDataClass('Abelardo', 'Carmona', 32)
    print()
except ValidationError as msj:
    print(msj)
"""2 validation errors for MyClass
0 # Look this enum error managment of the dataclass.
  String should have at most 5 characters [type=string_too_long, input_value='Abelardo', input_type=str]     
    For further information visit https://errors.pydantic.dev/2.5/v/string_too_long
1
  String should have at most 5 characters [type=string_too_long, input_value='Carmona', input_type=str]      
    For further information visit https://errors.pydantic.dev/2.5/v/string_too_long"""




model_config_for_dataclasse = ConfigDict(str_max_length=20) # This variable should be whatever we want.
# while with Basemodel classes MUST be 'model_config'.


### The same without error ###

@dataclass(config=model_config_for_dataclasse)
class MyPydanticDataClass:
    name: str
    surname: str
    age: int

try:
    object_2 = MyPydanticDataClass('Fernando', 'Carmona', 32)
    print(object_2)
except ValidationError as msj:
    print(msj)
"""MyPydanticDataClass(name='Fernando', surname='Carmona', age=32)"""
# Look the pydantic.dataclass output structure. It could be useful because the name of the class
# something that is different with basemodel classes.



### Let's try with dataclasses.dataclass from python ###

from dataclasses import dataclass

@dataclass(kw_only=False)
class MyOriginalDataclass:
    name: str 
    surname: str
    age: int

try:
    object_3 = MyOriginalDataclass('ak', 'Fernandez', 12)
    print(object_3)
except ValueError as ma:
    print(ma)
"""MyOriginalDataclass(name='ak', surname='Fernandez', age=12)"""
# The dataclass.dataclass output is the same as pydantic.dataclasses.dataclass.



### Extra ###
class NoExtra(BaseModel):
    model_config = ConfigDict(extra='forbid')
    name: str
    surname: str
    age: int


values = {'name': 'Yuri', 'surname': 'Suaza', 'age': 29, 'extra': 'extra value'}

try:
    object_4 = NoExtra(**values)
    print(object_4)
except ValidationError as msj:
    print(msj)
"""  Extra inputs are not permitted [type=extra_forbidden, input_value='extra value', input_type=str]
    For further information visit https://errors.pydantic.dev/2.5/v/extra_forbidden"""
# This output is indeed not allowing extra values.


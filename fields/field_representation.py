"""The parameter repr can be used to control whether the field should be included 
in the string representation of the model."""

from pydantic import BaseModel, Field


class User(BaseModel):
    name: str = Field(repr=True)  
    age: int = Field(repr=False)


user = User(name='John', age=42)
print(user)
#> name='John'



### exclude ###
# I see 'repr' and 'exclude' similar features, even though artificial inteligence couldn't tell me
# the differences between both concepts.

"""The exclude parameter can be used to control which fields should be excluded from the model when 
exporting the model.

See the following example:"""


from pydantic import BaseModel, Field


class User(BaseModel):
    name: str
    age: int = Field(exclude=True)


user = User(name='John', age=42)
print(user.model_dump())  
#> {'name': 'John'}





##### HERE WE HAVE THE DIFFERENCES ######

from pydantic import ValidationError


class ReprAndExcludeWithModelValidate(BaseModel):
    name: str = Field(exclude=True)
    surname: str = Field(repr=False)

try:
    kenifer = ReprAndExcludeWithModelValidate.model_validate({'name': 'kenifer', 'surname': 'Amariles'})
    print(kenifer.model_dump())
    """{'surname': 'Amariles'}""" # with model_dump() (json/dict output) exclude acts
except ValidationError as msj:
    print(msj)


class ReprAndExcludeWBasic(BaseModel):
    name: str = Field(exclude=True)
    surname: str = Field(repr=False)
    """name='ferna'""" # whithout model_dump() output repr acts.
try:
    ferna = ReprAndExcludeWBasic.model_validate({'name': 'ferna', 'surname': 'hernandez'})
    print(ferna)

except ValidationError as msj:
    print(msj)
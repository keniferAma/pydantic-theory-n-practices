## validation_alias with AliasPath ##

from pydantic import Field, AliasPath, BaseModel, field_validator, ValidationError
from pydantic_core import PydanticCustomError


class AliasPathClass(BaseModel):
    name: str = Field(validation_alias=AliasPath('names', 0))
    surname: str = Field(validation_alias=AliasPath('names', 1))


    @field_validator('name', 'surname')
    @classmethod
    def names_validation(cls, values: str):
        if not values.startswith('S'):
            raise PydanticCustomError(
                'names_validation_error',
                'The name and surname must start with "S"'
            )

        return values

try:
    user_1 = AliasPathClass.model_validate({'names': ['Salejandro', 'Sernandez']})
    print(user_1)

except ValidationError as msj:
    print(msj)



# Now trying without AliasPath.

class ValidationAlias(BaseModel):
    name: str = Field(validation_alias='name')
    surname: str = Field(validation_alias='surname')

    @field_validator('name', 'surname')
    @classmethod
    def name_and_surname_validation(cls, values):
        if not values.startswith('j'):
            raise PydanticCustomError(
                'name_and_surname_validator_error',
                'the name and the surname should start with "j"'
            )
        return values
    
try:
    user_2 = ValidationAlias(name='Gildardo', surname=('Montoya'))

except ValidationError as message:
    print(message)




### strings and numeric constraints ###
    
from decimal import Decimal # If we're working with max_digits we have to import Decimal.
    
class NumericConstraints(BaseModel):
    min_length_value: str = Field(min_length=2, max_length=12)
    max_digits_value: Decimal = Field(max_digits=5, decimal_places=3)
    # 'max_digits' is the total amount, while 'decimal_places' are the ones after the comma.
    pattern: str = Field(pattern=r'^[a-zA-Z]{2,}@(gmail|hotmail|outlook)\.(com|es)$')

    
 

try:
    user_3 = NumericConstraints.model_validate({'min_length_value': 'alejandro',
                                                'max_digits_value': '2.2',
                                                'pattern': 'kenifer@hotmail.com'}, strict=True)
    # Remember when we use 'strict=True' we are telling pydantic to be stricted with numbers on this case
    # due to we are passing a string with decimal numbers. If strict mode was not there, the decimal string
    # could be easily parse.
    print(user_3)

except ValidationError as msj:
    print(msj)



### repr vs exclude in Field ###
    
class ReprAndExclude(BaseModel):
    name: str = Field(exclude=True)
    surname: str = Field(repr=False)
    """{'surname': 'Amariles'}""" # as we can see, the repr=False was 

try:
    kenifer = ReprAndExclude.model_validate({'name': 'kenifer', 'surname': 'Amariles'})
    print(kenifer.model_dump())

except ValidationError as msj:
    print(msj)



### model_json_schema exercise ###
# To remeber, a model json schema is used as a detailed description purposes.
    
class Student(BaseModel):
    name: str = Field(default='User', description='This is the user name')
    surname: str = Field(init_var=False, alias='last_name')


student_1 = Student.model_validate({'name': 'Salome', 'last_name': 'Bedoya'})
print(student_1.model_json_schema())
print(student_1.model_dump())
print(student_1.model_json_schema(by_alias=True))


"""{
    'properties': {
        'name': {'default': 'User', 
        'description': 'This is the user name', 
        'title': 'Name', 'type': 'string'}, 
        'last_name': {'title': 'Last Name', 'type': 'string'}
        }, 
    'required': ['last_name'], 
    'title': 'Student', 
    'type': 'object'
    }
    """
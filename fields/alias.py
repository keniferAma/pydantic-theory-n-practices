# alias
from pydantic import BaseModel, Field


class User(BaseModel):
    name: str = Field(..., alias='username')


user = User(username='johndoe')  
print(user)
#> name='johndoe'
print(user.model_dump(by_alias=True))  
#> {'username': 'johndoe'}





# validation_alias

class UserValidation(BaseModel):
    name_for_validation: str = Field(..., validation_alias='username')


user_validation = UserValidation(username='johndoe')  
print(user_validation)
#> name_for_validation='johndoe'
print(user_validation.model_dump(by_alias=True))  
#> {'name_for_validation': 'johndoe'} #### validation_alias with json or dictionaries files, gives us the 
# attribute name as key.




# serialization_alias 

class UserSerialization(BaseModel):
    name_for_serialization: str = Field(..., serialization_alias='username')


user_serialization = UserSerialization(name_for_serialization='johndoe') # serialization_alias does not allow
# us to give the alias as attribute.

print(user_serialization)
#> name_for_serialization='johndoe'
print(user_serialization.model_dump(by_alias=True))  
#> {'username': 'johndoe'}



# THIS IS ONE EXAMPLE DONE BY ARTIFICIAL INTELIGENCE WITH AN ESCENARIO WHERE THIS ALIAS COULD BE HELPFUL:

from pydantic import BaseModel, Field

class User(BaseModel):
    user_id: int = Field(alias='userId')
    first_name: str = Field(alias='firstName')
    last_name: str = Field(alias='lastName')
    email_address: str = Field(alias='emailAddress')

# API response
api_response = {
    'userId': 1,
    'firstName': 'John',
    'lastName': 'Doe',
    'emailAddress': 'john.doe@example.com'
}

# Create a User instance from the API response
user = User(**api_response)

# Now you can access the fields using snake_case
print(user.user_id)  # Output: 1
print(user.first_name)  # Output: John
print(user.last_name)  # Output: Doe
print(user.email_address)  # Output: john.doe@example.com

# and as we can see, this escenario gives us information that comes from a database with the same names from 
# the database names and the alias names of our class, then once executed, we can manage that information at will
# with the names we wanted as field_names.
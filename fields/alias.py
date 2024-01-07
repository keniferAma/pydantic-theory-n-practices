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




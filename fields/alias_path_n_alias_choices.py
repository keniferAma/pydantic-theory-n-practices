from pydantic import BaseModel, Field, AliasPath


class User(BaseModel):
    first_name: str = Field(validation_alias=AliasPath('names', 0))
    last_name: str = Field(validation_alias=AliasPath('names', 1))

user = User.model_validate({'names': ['John', 'Doe']})  
print(user)
#> first_name='John' last_name='Doe'
### As we can see in the AliasPath we are giving an alias for both attributes which is 'names',
### then, we are giving an index as second value, so once we give the arguments, the index 0 = first_name
### and the index 1 = last_name (on this case of course)



# This is how regurarly a model_validate entry works.
class ModelValidate(BaseModel):
    name: str
    surname: str


user_3 = ModelValidate.model_validate({'name': 'alejandro', 'surname': 'fernandez', 'age': '12'})
print(user_3)




class Survey(BaseModel):
    logo_url: str = Field(..., validation_alias=AliasPath('logo', 'url'))

a = Survey(**{'logo': {'url': 'foo'}})
print(a.logo_url)  # Output: 'foo'

# Always remember that the first argument given to either AliasPath or whatever alias, is the alias name,
# that means that is the reeplace of the field name.




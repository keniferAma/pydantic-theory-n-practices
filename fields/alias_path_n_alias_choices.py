from pydantic import BaseModel, Field, AliasPath


class User(BaseModel):
    first_name: str = Field(validation_alias=AliasPath('names', 0))
    last_name: str = Field(validation_alias=AliasPath('names', 1))

user = User.model_validate({'names': ['John', 'Doe']})  
print(user)
#> first_name='John' last_name='Doe'
### As we can see in the AliasPath we are giving an alias for both attributes which is 'names',
### then, we are giving an index as second value, so once we give the arguments, the index 0 = first_name
### and the index 1 = last_name (on this case of course) ALL THIS IN CASE WE ARE PROVIDING LISTS AS DATA TO VALIDATE.
### ON THE OTHER HAND WE CAN USE JSON AND DICTIONARY DATA TO PARSING DATA.



# This is how regurarly a model_validate entry works.
class ModelValidate(BaseModel):
    name: str
    surname: str


user_3 = ModelValidate.model_validate({'name': 'alejandro', 'surname': 'fernandez', 'age': '12'})
print(user_3)




class Survey(BaseModel):
    logo_url: str = Field(..., validation_alias=AliasPath('logo', 'url')) 
    # When we are using strings from the second parameter on out (en adelante), that means that the nest goes further.
    # This es an example provided by bing:

a = Survey(**{'logo': {'url': 'foo'}})
print(a.logo_url)  # Output: 'foo'

# Always remember that the first argument given to either AliasPath or whatever alias, is the alias name,
# that means that is the reeplace of the field name.
"""For example, if your data looks like this: {'company': {'logo': {'url': 'foo'}}}, 
you could use AliasPath('company', 'logo', 'url') to tell Pydantic to look for the 
logo_url field at data['company']['logo']['url']."""


## AliasChoices ##
### BASICALLY THIS FEATURE ALLOW US TO CHOOSE MORE THAN ONE ALIAS FOR THE SAME FIELD. ###
from pydantic import AliasChoices


class User(BaseModel):
    first_name: str = Field(validation_alias=AliasChoices('first_name', 'fname')) # These are the alias choices por the field.
    last_name: str = Field(validation_alias=AliasChoices('last_name', 'lname'))

user = User.model_validate({'fname': 'John', 'lname': 'Doe'})  
print(user)
#> first_name='John' last_name='Doe'
user = User.model_validate({'first_name': 'John', 'lname': 'Doe'})  
print(user)
#> first_name='John' last_name='Doe'

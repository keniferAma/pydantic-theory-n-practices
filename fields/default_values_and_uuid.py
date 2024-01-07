# basics of default values in fields #
# default #

from pydantic import BaseModel, Field


class User(BaseModel):
    name: str = Field(default='John Doe') # this is a static field


user = User()
print(user)
#> name='John Doe'



# default_factory #

from uuid import uuid4 # this is a librery to generate universal identifiers. This is the most common version.
# (Universal Unique Identifier) also known as GUID.
# It is used to identify databases, primary keys, bluetooth profiles
# It is divided in secuences of 8-4-4-4-12 digits, it means 32 hexadecimal digits
# In databases is common to see the uuid version 1. specially to name the primary_keys instead of an AUTO_INCREMENT
# number.
"""The first group of 8 digits is the time_low field.
The second group of 4 digits is the time_mid field.
The third group of 4 digits is the time_hi_and_version field.
The fourth group of 4 digits is the clock_seq_hi_and_res and clock_seq_low fields.
The last group of 12 digits is the node field."""
# NOTE: this 8-4-4-4-12 is a format to represent for human readability only, but the execution manner could be different.

from pydantic import BaseModel, Field


class UserDefaultFactory(BaseModel):
    id: str = Field(default_factory=lambda: uuid4().hex) # this is a dinamic data.

default_factory_user = UserDefaultFactory()
print(default_factory_user)
#id='4610f55ad86d4401999f3a11a16182a9' 


# The main difference between 'default' and 'default_factory' is that 'default' is allowed with static data
# such us strings, integers, lists, tuples, etc... while 'default_factory' is more accurate for dinamic data
# such us callables, datetime, functions, classes etc, this last one deals with data that changes at other place
# of the program.
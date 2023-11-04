### some theory related with the topic InstanceOf ###

from typing import List

from pydantic import BaseModel, InstanceOf, ValidationError


class Fruit:
    def __repr__(self):
        return self.__class__.__name__


class Banana(Fruit):
    ...


class Apple(Fruit):
    ...


class Basket(BaseModel):
    fruits: List[InstanceOf[Fruit]] # we're defining that the field "fruits" MUST be a list of "Fruit" instances.


print(Basket(fruits=[Banana(), Apple()])) # we're defining Fruit instances
#> fruits=[Banana, Apple]
try:
    Basket(fruits=[Banana(), 'Apple'])
except ValidationError as e:
    print(e)
    """
    1 validation error for Basket
    fruits.1
      Input should be an instance of Fruit [type=is_instance_of, input_value='Apple', input_type=str]
    """

# I think this is only a way of "isinstance" that pydantic manipulates to parse data as its typing methods.
# In this case if a given argument is not an instances of what we want, so pydantic will run an error.



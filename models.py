from pydantic import BaseModel


class User(BaseModel):
    id: int
    name: str = 'Jane Doe'
    


user = User(id='123') # Recién noto que si es necesario asignar clave, valor para los argumentos dados a la clase.
assert isinstance(user.id, int) # Reafirmando la versatilidad de pydantic con respecto al tipado:
# Dimos como argumento un string con números, mas sin embargo al hacer el "assert" no arroja error, pese a asignar
# en isinstance como "int"


print(user.model_fields_set)
"""{'id'}"""
# Al parecer esta opcion nos muestra, como podemos intuir por su nombre, los campos que SON OBLIGATORIOS 
# y además los imprime en formato diccionario. No aparece el campo "name" por obvias razones.

assert user.model_dump() == {'id': 123, 'name': 'Jane Doe'}
# Como ya lo hemos estudiado, model_dumb nos retorna un diccionario con los campos del objeto y sus valores.
"""Either .model_dump() or dict(user) will provide a dict of fields, but .model_dump() 
can take numerous other arguments. (Note that dict(user) will not recursively convert nested models 
into dicts, but .model_dump() will.)"""
# Al parecer con model_dump vamos a tener un mejor rendimiento en cuanto a anidación, recordemos que anidación es 
# la organización jerargica de la información, por ejemplo un bucle for dentro de otro, o una lista dentro de otra lista

### EN ESTE EJEMPLO INTENTAMOS COMPROBAR LO ANTERIOR SIN EMBARGO EL RESULTADO FUÉ EL MISMO, DEBEMOS SUPONER QUE ESTOS B
### BENEFICIOS DE ANIDACIÓN SE VERÁN REFLEJADOS EN SITUACIONES MÁS COMPLEJAS.

class User(BaseModel):
    id: int
    name: dict = 'Jane Doe'


user = User(id='123', name={'humano':{'first': 'carlos', 'second': 'hernandez'}})
print(user.model_dump())
print(dict(user))
## RESUTADO :
{'id': 123, 'name': {'humano': {'first': 'carlos', 'second': 'hernandez'}}}
{'id': 123, 'name': {'humano': {'first': 'carlos', 'second': 'hernandez'}}}
## SON COMPLETAMENTE IGUALES.






                                            ### BASIC MODELS ###
## model_construct:

class User(BaseModel):
    id: int
    age: int
    name: str = 'John Doe'


original_user = User(id=123, age=32)

user_data = original_user.model_dump()
print(user_data)
#> {'id': 123, 'age': 32, 'name': 'John Doe'}
fields_set = original_user.model_fields_set
print(fields_set)
#> {'age', 'id'}

# ...
# pass user_data and fields_set to RPC or save to the database etc.
# ...

# you can then create a new instance of User without
# re-running validation which would be unnecessary at this point:
new_user = User.model_construct(_fields_set=fields_set, **user_data)
print(repr(new_user))
#> User(id=123, age=32, name='John Doe')
print(new_user.model_fields_set)
#> {'age', 'id'}

# construct can be dangerous, only use it with validated data!: ### PONER MUCHO CUIDADO CON ESTA ADVERTENCIA.
bad_user = User.model_construct(id='dog')
print(repr(bad_user))
#> User(id='dog', name='John Doe')




############ PROBANDO UNA MANERA QUE NO CONOCÍA, DE INGRESAR LOS ARGUMENTOS A LA INSTANCIA.
pruebilla = User={'id': 2, 'age': 3}
print(repr(pruebilla))








                            ######## ANIDACIONES ENTRE VARIAS CLASES (método tradicional)######

from typing import List, Optional

from pydantic import BaseModel


class Foo(BaseModel):
    count: int
    size: Optional[float] = None


class Bar(BaseModel):
    apple: str = 'x'
    banana: str = 'y'


class Spam(BaseModel):
    foo: Foo
    bars: List[Bar]


m = Spam(foo={'count': 4}, bars=[{'apple': 'x1'}, {'apple': 'x2'}]) # Para tener en cuenta la manera como se entran 
# los argumentos.
print(m)
"""
foo=Foo(count=4, size=None) bars=[Bar(apple='x1', banana='y'), Bar(apple='x2', banana='y')]
"""
print(m.model_dump())
"""
{
    'foo': {'count': 4, 'size': None},
    'bars': [{'apple': 'x1', 'banana': 'y'}, {'apple': 'x2', 'banana': 'y'}],
}
"""                            







                                            ###### model_rebuild() ########
# Debemos tener en cuenta que estamos usando de ejemplo muchas de las clases del inicio del programa, entonces no vamos 
# a generar los mismo errores.

from pydantic import BaseModel, PydanticUserError


class Foo(BaseModel):
    x: 'Bar' # Estamos anidando una clase que aún no está creada.

try:
    Foo.model_json_schema() # Intentamos obtener la información detallada de la clase, sin embargo nos va a arrojar error.
except PydanticUserError as e: # Tener en cuenta que estamos usando un detector de error en específico.
    print(e)
    """
    `Foo` is not fully defined; you should define `Bar`, then call `Foo.model_rebuild()`.

    For further information visit https://errors.pydantic.dev/2/u/class-not-fully-defined
    """


class Bar(BaseModel): # Creamos ahora si la clase que nos hacía falta desde un principio.
    pass


Foo.model_rebuild() # usamos nuestro protagonista para reconstruir, como lo dice su palabra, la solicitud que necesitamos.
print(Foo.model_json_schema())
"""
{
    '$defs': {'Bar': {'properties': {}, 'title': 'Bar', 'type': 'object'}},
    'properties': {'x': {'$ref': '#/$defs/Bar'}},
    'required': ['x'],
    'title': 'Foo',
    'type': 'object',
}
"""

# Ahora vamos a intentar replicar este ejercicio, de manera que nos quede un poco mas claro de que se trata.

class Rebuild(BaseModel):
    name: str
    age: 'Age'

try:
    Rebuild.model_json_schema()
except PydanticUserError as e:
    print(e)
    """`Rebuild` is not fully defined; you should define `Age`, then call `Rebuild.model_rebuild()`."""

#Creamos la clase, pero después del código, para que nos continúe arrojando el error.
class Age(BaseModel):
    pass


Rebuild.model_rebuild()
print(Rebuild.model_json_schema())
"""{
        '$defs': {'Age': {'properties': {}, 'title': 'Age', 'type': 'object'}}, 
        'properties': {
            'name': {'title': 'Name', 'type': 'string'}, 
            'age': {'$ref': '#/$defs/Age'}}, 'required': ['name', 'age'], 
            'title': 'Rebuild', 'type': 'object'
}"""
# Algo para tener muy en cuenta: en el try-except igualmente nos continúa arrojando el error, sin embargo, al reconstruir
# el objeto mediante model_rebuild, es como si estuvieramos llamando al objeto mas abajo del código, donde ahora si va a
# aceptar la clase recien creada, y por consiguiente nos va a dejar imprimir el json informativo model_json_schema()
# ALGO IMPORTANTE: NO HE ENCONTRADO EL VERDADERO USO DE ÉSTE MODELO. CON O SIN ÉL, TENEMOS EL MISMO RESULTADO.











                        #### ANIDADO CON CLASES SIN basemodel Y USANDO ConfigDict


from typing import List

from pydantic import BaseModel, ConfigDict

# Para este ejemplo pydantic ha usado clases con la sintaxis tradicional.
# El asterisco "*" cuando va en estas clases, nos está indicando que, al pasar los argumentos directamente
# estos deben llevar obligatoriamente, su parametro, es decir, deben llevar "name=", "species="

# Lo que puedo concluir acerca del uso de "model_config = ConfigDict(from_attributes=True)" es el uso para anidar 
# instancias de objetos tradicionales (hechos sin basemodel), en objetos tipo basemodel, con la condición exclusiva
# de que ambos objetos (el de basemodel y tradicional) deben tener los mismos argumentos, correctamente tipados y bien
# definida la configuración model_config = ConfigDict(from_attributes=True) en el objeto "clon" (disponible a anidar)
# y en el objeto anidado.
# NOTA: esto solo podrá ser posible usar mediante la instancia del objeto tradicional, y no anidando dicho objeto 
# a nuestro objeto basemodel.

class PetCls: 
    def __init__(self, *, name: str, species: str): 
        self.name = name
        self.species = species


class PersonCls:
    def __init__(self, *, name: str, age: float = None, pets: List[PetCls]):
        self.name = name
        self.age = age
        self.pets = pets # Debemos tener la misma cantidad de atributos a los del objeto que vamos a usar de anidador
        # es decir, en este caso 2 atributos, ya que "age" lo tenemos de manera opcional.


class Pet(BaseModel):
    model_config = ConfigDict(from_attributes=True)# objeto anidado y anidador deben ser los de basemodel
    # además de que deben llevar si o si ambos model_config.

    name: str
    species: str 


class Person(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    age: float = None
    pets: List[Pet] 


bones = PetCls(name='Bones', species='dog') # Objeto creados con clases tradicionales.
orion = PetCls(name='Orion', species='cat') # Otro objeto hecho con clase tradicional.
anna = PersonCls(name='Anna', age=20, pets=[bones, orion]) # en "pet" asignamos la variable del objeto tradicional.
anna_model = Person.model_validate(anna)
print(anna_model)
"""
name='Anna' age=20.0 pets=[Pet(name='Bones', species='dog'), Pet(name='Orion', species='cat')]
"""








                            ##### ValidationError ######

# Como ya previamente lo habíamos visto, ValidationError nos propociona información adicional relacionada al fallo
# que estamos presentando.


from typing import List

from pydantic import BaseModel, ValidationError


class Model(BaseModel):
    list_of_ints: List[int]
    a_float: float


data = dict(
    list_of_ints=['1', 2, 'bad'], # Aquí estamos simulando el error.
    a_float='not a float', # Aquí debería haber un bool.
)

try:
    Model(**data)
except ValidationError as e:
    print(e)
    """
    2 validation errors for Model
    list_of_ints.2
      Input should be a valid integer, unable to parse string as an integer [type=int_parsing, input_value='bad', input_type=str]
    a_float
      Input should be a valid number, unable to parse string as a number [type=float_parsing, input_value='not a float', input_type=str]
    """










                        ### model_validate model_validate_json #####

# Como ya lo hemos estudiado, model_validate nos recibe informacion en formato json o diccionario, mientras que
# model_validate_json nos recibe el mismo diccionario pero en formato repr, es decir como string.

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ValidationError


class User(BaseModel):
    id: int
    name: str = 'John Doe'
    signup_ts: Optional[datetime] = None


m = User.model_validate({'id': 123, 'name': 'James'})
print(m)
#> id=123 name='James' signup_ts=None

try:
    User.model_validate(['not', 'a', 'dict'])
except ValidationError as e:
    print(e)
    """
    1 validation error for User
      Input should be a valid dictionary or instance of User [type=model_type, input_value=['not', 'a', 'dict'], input_type=list]
    """

m = User.model_validate_json('{"id": 123, "name": "James"}')
print(m)
#> id=123 name='James' signup_ts=None

try:
    m = User.model_validate_json('{"id": 123, "name": 123}')
except ValidationError as e:
    print(e)
    """
    1 validation error for User
    name
      Input should be a valid string [type=string_type, input_value=123, input_type=int]
    """

try:
    m = User.model_validate_json('Invalid JSON')
except ValidationError as e:
    print(e)
    """
    1 validation error for User
      Invalid JSON: expected value at line 1 column 1 [type=json_invalid, input_value='Invalid JSON', input_type=str]
    """








                                ### model_construct ###
# what I've learned about this model is that we can create a new instance without setting the arguments and 
# the values again, without validating.
# On this example we are going to use the output of model_validate and model_fields_set, wich will give us the 
# the output in a json format, wich in logic terms it would not be posible at all, buy with model_construct do.

from pydantic import BaseModel


class User(BaseModel):
    id: int
    age: int
    name: str = 'John Doe'


original_user = User(id=123, age=32)

user_data = original_user.model_dump()
print(user_data)
#> {'id': 123, 'age': 32, 'name': 'John Doe'}
fields_set = original_user.model_fields_set
print(fields_set)
#> {'age', 'id'}

# ...
# pass user_data and fields_set to RPC or save to the database etc.
# ...

# you can then create a new instance of User without
# re-running validation which would be unnecessary at this point:
new_user = User.model_construct(_fields_set=fields_set, **user_data) # Here we set the arguments from some outputs.
# and the creator gives us some advices about how to manage this kind of models. because of it's nature.
print(repr(new_user))
#> User(id=123, age=32, name='John Doe')
print(new_user.model_fields_set)
#> {'age', 'id'}

# construct can be dangerous, only use it with validated data!:
bad_user = User.model_construct(id='dog')
print(repr(bad_user))
#> User(id='dog', name='John Doe')


## IMPORTANT:
#The _fields_set keyword argument to model_construct() is optional, 
# but allows you to be more precise about which fields were originally set and which weren't. 
# If it's omitted model_fields_set will just be the keys of the data provided.
#For example, in the example above, if _fields_set was not provided, new_user.model_fields_set 
# would be {'id', 'age', 'name'}.
# Casualy this information contrasts with the probe I was doing some seconds ago.









                            ##### GENERIC MODELS #####
"""Pydantic supports the creation of generic models to make it easier to reuse a common model structure.

In order to declare a generic model, you perform the following steps:

Declare one or more typing.TypeVar instances to use to parameterize your model.
Declare a pydantic model that inherits from pydantic.BaseModel and typing.Generic, where you pass the TypeVar instances as parameters to typing.Generic.
Use the TypeVar instances as annotations where you will want to replace them with other types or pydantic models.
Here is an example using a generic BaseModel subclass to create an easily-reused HTTP response payload wrapper:"""


from typing import Generic, List, Optional, TypeVar

from pydantic import BaseModel, ValidationError

DataT = TypeVar('DataT') # we are defining the value to inherit.
# as the type says, it's type variable. we are defining a varable of type Type.


class Error(BaseModel):
    code: int
    message: str

class DataModel(BaseModel):
    numbers: List[int]
    people: List[str]

class Response(BaseModel, Generic[DataT]): # using "Generic" with the inherited value. BUT NOT NECCESARY
    # BECAUSE WE CAN ALSO USE List, or whatever. but in this case we used Generic, as the word itself says,
    # to create a generic inherit value, where we can set the type values at will.
    data: Optional[DataT] = None # Defining that the value will be Optional type.


data = DataModel(numbers=[1, 2, 3], people=[])
error = Error(code=404, message='Not found')

print(Response[int](data=1)) # IT IS NECCESARY TO SET THE TIPE VALUE AMONG BRACKETS WHEN USING TypeVar
# AND THAT'S BECAUSE OF THE TypeVar NATURE, IF WE DON'T, WE WOULD BE JUST USING Basemodel.
#> data=1
print(Response[str](data='value')) # Here we defined 
#> data='value'
print(Response[str](data='value').model_dump())
#> {'data': 'value'}
print(Response[DataModel](data=data).model_dump())
#> {'data': {'numbers': [1, 2, 3], 'people': []}}
try:
    Response[int](data='value') # Here we are forcing an error.
except ValidationError as e:
    print(e)
    """
    1 validation error for Response[int]
    data
      Input should be a valid integer, unable to parse string as an integer [type=int_parsing, input_value='value', input_type=str]
    """

### we can also create a subclass inheriting from TypeVar

TypeX = TypeVar('TypeX')


class BaseClass(BaseModel, Generic[TypeX]):
    X: TypeX


class ChildClass(BaseClass[TypeX], Generic[TypeX]): # this is the subclass or the childclass.
    # Inherit from Generic[TypeX]
    pass


# Replace TypeX by int
print(ChildClass[int](X=1))
#> X=1








                            #### GENERIC MODELS NESTING ####
from typing import Generic, TypeVar

from pydantic import BaseModel, ValidationError

T = TypeVar('T')


class InnerT(BaseModel, Generic[T]):
    inner: T


class OuterT(BaseModel, Generic[T]):
    outer: T
    nested: InnerT[T]


nested = InnerT[int](inner=1)
print(OuterT[int](outer=1, nested=nested))
#> outer=1 nested=InnerT[int](inner=1)
try:
    nested = InnerT[str](inner='a')
    print(OuterT[int](outer='a', nested=nested)) # forcing an error, set as "int", but giving "str"
except ValidationError as e:
    print(e)
    """
    2 validation errors for OuterT[int]
    outer
      Input should be a valid integer, unable to parse string as an integer [type=int_parsing, input_value='a', input_type=str]
    nested
      Input should be a valid dictionary or instance of InnerT[int] [type=model_type, input_value=InnerT[str](inner='a'), input_type=InnerT[str]]
    """








                            ### SETTING A BOUND/RESTRICTION INSIDE THE TypeVar ###

from typing import Generic, TypeVar

from pydantic import BaseModel, ValidationError

AT = TypeVar('AT') # On this varibles, we are not setting any restriccion or bound.
BT = TypeVar('BT')


class Model(BaseModel, Generic[AT, BT]):
    a: AT
    b: BT


print(Model(a='a', b='a'))
#> a='a' b='a'

IntT = TypeVar('IntT', bound=int) # Right here we set up a bound = int, that means that the value MUST be int.
typevar_model = Model[int, IntT] # Look how we saved the class in a variable without setting the arguments.
print(typevar_model(a=1, b=1)) # In efect we give the values as int
#> a=1 b=1
try:
    typevar_model(a='a', b='a') # This is going to be an error.
except ValidationError as exc:
    print(exc)
    """
    2 validation errors for Model[int, ~IntT]
    a
      Input should be a valid integer, unable to parse string as an integer [type=int_parsing, input_value='a', input_type=str]
    b
      Input should be a valid integer, unable to parse string as an integer [type=int_parsing, input_value='a', input_type=str]
    """

concrete_model = typevar_model[int]
print(concrete_model(a=1, b=1))
#> a=1 b=1







                        #### USING "SerializeAsAny" in generic models ####

from typing import Generic, TypeVar

from pydantic import BaseModel, SerializeAsAny


class Model(BaseModel):
    a: int = 42


class DataModel(Model):
    b: int = 2
    c: int = 3


BoundT = TypeVar('BoundT', bound=Model)


class GenericModel(BaseModel, Generic[BoundT]):
    data: BoundT


class SerializeAsAnyModel(BaseModel, Generic[BoundT]):
    data: SerializeAsAny[BoundT]


data_model = DataModel()

print(GenericModel(data=data_model).model_dump())
#> {'data': {'a': 42}}


print(SerializeAsAnyModel(data=data_model).model_dump())
#> {'data': {'a': 42, 'b': 2, 'c': 3}}
### AS WE CAN SEE, BY DOING THIS WAY WE CAN GET AN OUTPUT OF THE ENTIRE FIELDS, EVEN EXTRA FIELDS.









                                    ### DINAMIC MODEL CREATION ###
### Basically another way to crate a model.
"""In summary, whether to use create_model or define a new class that inherits from 
BaseModel depends on your specific use case. If you need to create models with fields or 
validators that are not known until runtime, create_model may be a good choice. Otherwise, 
defining a new class that inherits from BaseModel may be a better option."""

from pydantic import BaseModel, create_model, field_validator

DynamicFoobarModel = create_model(
    'DynamicFoobarModel',
    foo=(str, ...), 
    bar=(int, 123)# After a "coma" we set the default values.
)   # Look at the model structure and the way how to set the fields.


class StaticFoobarModel(BaseModel):
    foo: str
    bar: int = 123

# Both classes are identical in structure model.



"""Fields are defined by a tuple of the form (<type>, <default value>). 
The special keyword arguments __config__ and __base__ can be used to customise the new model. 
This includes extending a base model with extra fields."""

from pydantic import BaseModel, create_model


class FooModel(BaseModel):
    foo: str
    bar: int = 123
    
    
    

BarModel = create_model( ## LOOK THAT THIS IS NOT USING Basemodel.
    'BarModel',
    apple=(str, 'russet'),
    banana=(str, 'yellow'),
    __base__=FooModel, # with dinamic models we use "=" instead of ":" to type.
    # But in this case "__base__" is not a "key" in the field.
    # It is like we are including the fields of class "FooModel" to this dinamic model, and that through "__base__"
)   # IT'S LIKE THE EQUIVALENT TO INHERITING FIELDS FROM OTHER OBJECTS.
print(BarModel)
#> <class 'pydantic.main.BarModel'>
print(BarModel.model_fields.keys()) 
#> dict_keys(['foo', 'bar', 'apple', 'banana'])
# We got the FooModel fields through __base__ # IT'S LIKE THE EQUIVALENT TO INHERITING FIELDS FROM OTHER OBJECTS.










                                    ### field_validator ###
"""In summary, whether to use create_model or define a new class that inherits from 
BaseModel depends on your specific use case. If you need to create models with fields or 
validators that are not known until runtime, create_model may be a good choice. Otherwise, 
defining a new class that inherits from BaseModel may be a better option."""

from pydantic import ValidationError, create_model, field_validator


def username_alphanumeric(cls, v):
    assert v.isalnum(), 'must be alphanumeric' # This is the string to advice an error.
    return v


validators = {
    'username_validator': field_validator('username')(username_alphanumeric)
}       # Here we have to be cautious at the field_validator structure.
        # First is the key of the field to validate, then the function that works with the validator.
        # Notice that the field_validator arguments are in separated parentesis.

UserModel = create_model(
    'UserModel',
    username=(str, ...), #the 3 non-stop dots means OBLIGATORY field.
    __validators__=validators # "__validators__" is used more as type meaning, and then we have
    # the "validator" variable that contains the dictionary with the decorator field_validator
)   # THINKING CAREFULLY, __validator__ IS NOT A key-value FIELD, IT IS MORE LIKE AS IT IS, A VALIDATOR FIELD
    # Analyzing this structure we realize that __validator__ is like a bridge among the dinamic field and 
    # the DICTIONARY "validators" witch is the escense of any pydantic or dataclass model.
    # REMEBER THAT COMMONLY validators ARE SET AS @validators AND AS METHOD. HERE WE ARE DOING THE SAME BUT
    # WITH create_model()

user = UserModel(username='scolvin')
print(user)
#> username='scolvin'
print(user.model_fields.keys())
#dict_keys(['username']) Only show us the "username" key, not the "username_validator" (maybe are we missing __base__)?


try:
    UserModel(username='scolvi%n') # induced error. the validator function espects an alphanumeric field.
except ValidationError as e:
    print(e)
    """
    1 validation error for UserModel
    username
      Assertion failed, must be alphanumeric [type=assertion_error, input_value='scolvi%n', input_type=str]
    """







                                        ### RootModel ###

"""The root type can be any type supported by Pydantic, and is specified by the 
generic parameter to RootModel. The root value can be passed to the model __init__ 
or model_validate as via the first and only argument.

This can be useful in situations where you need to validate data that does not have a natural 
key-value structure, such as a list or a scalar value."""                        

from typing import Dict, List

from pydantic import RootModel

Pets = RootModel[List[str]] # this is not a natural key-word structure.
PetsByName = RootModel[Dict[str, str]]


print(Pets(['dog', 'cat'])) # sending list, and not a key-word structure.
#> root=['dog', 'cat']
print(Pets(['dog', 'cat']).model_dump_json())
#> ["dog","cat"]
print(Pets.model_validate(['dog', 'cat'])) # It is posible setting lists with model_validate and RootModels.
#> root=['dog', 'cat']
print(Pets.model_json_schema())
"""
{'items': {'type': 'string'}, 'title': 'RootModel[List[str]]', 'type': 'array'}
"""

print(PetsByName({'Otis': 'dog', 'Milo': 'cat'}))
#> root={'Otis': 'dog', 'Milo': 'cat'}
print(PetsByName({'Otis': 'dog', 'Milo': 'cat'}).model_dump_json())
#> {"Otis":"dog","Milo":"cat"}
print(PetsByName.model_validate({'Otis': 'dog', 'Milo': 'cat'}))
#> root={'Otis': 'dog', 'Milo': 'cat'}        










                                        ### HOW TO ITERATE FROM RootModel ###

from typing import List

from pydantic import RootModel


class Pets(RootModel): # We can inherit "RootModel" directly from the class.
    ## IMPORTANT: THE FUNCTIONS BELOW DOESN'T WORK INHERITING FROM basemodel.
    root: List[str]

    def __iter__(self):
        return iter(self.root) # "iter" is, as we can see, a function. 

    def __getitem__(self, item): # THIS KIND OF FUNCTIONS WORKS INMEDIATLY WITHOUT CALLING THEM.
    # THA'S HOW, FOR EXAMPLE "__repr__" WORKS. ON THIS EXAMPLES, IF WE WANT TO ITERATE THE INFROMATION GIVEN
    # TO THIS CLASS, WE ONLY HAVE TO USE "for" ITERATOR, ONCE WE DO THAT, AUTOMATICALLY __iter__ FUNCTION WORKS.
    # THE SAME HAPPENS  WITH __getitem__ ONCE WE TRY TO SEARCH WHATEVER OF THE LIST O ELEMENTS BY ITS INDEX.
        return self.root[item]


pets = Pets.model_validate(['dog', 'cat'])
print(pets[0]) # Here we get the value we want, and that's posible thanks to "__getitem__"
#> dog
print([pet for pet in pets]) # This is posible because of the __iter__ parameter is set up.
#> ['dog', 'cat']










                        ### CREATING SUBCLASSES WITH RootModel ###
from typing import List

from pydantic import RootModel


class Pets(RootModel[List[str]]):
    """specifying the root type as List[str] when subclassing RootModel tells 
    pydantic what type of data the model should expect as its root value, 
    while defining the root field as being of type List[str] provides a way 
    to access and manipulate this data within the model’s methods. """
    root: List[str]

    def describe(self) -> str:
        return f'Pets: {", ".join(self.root)}'


my_pets = Pets.model_validate(['dog', 'cat'])

print(my_pets.describe())
#> Pets: dog, cat


### ANOTHER EXAMPLE

from pydantic import RootModel, conint
from typing import List

class IntList(RootModel[List[conint(ge=0)]]):
    pass

data = [1, 2, 3]
model = IntList(data) # look the way we send the information, directly without unpacking. AS ALWAYS.
print(model.root)  # [1, 2, 3]
                










                               #### FAUX IMMUTABILITY ###  
#Models can be configured to be immutable via model_config['frozen'] = True. 


from pydantic import BaseModel, ConfigDict, ValidationError


class FooBarModel(BaseModel):
    model_config = ConfigDict(frozen=True) # to remember, with python dataclasses this is made in the decorator.

    a: str
    b: dict


foobar = FooBarModel(a='hello', b={'apple': 'pear'})

try:
    foobar.a = 'different'# Here we are trying to change the value, but it is imposible while model_config is frozen
except ValidationError as e:
    print(e)
    """
    1 validation error for FooBarModel
    a
      Instance is frozen [type=frozen_instance, input_value='different', input_type=str]
    """

print(foobar.a)
#> hello
print(foobar.b)
#> {'apple': 'pear'}
foobar.b['apple'] = 'grape' # But it seems it's posible to make changes with dictionaries.
print(foobar.b)
#> {'apple': 'grape'}








                                        ### ClassVar ###
"""Attributes annotated with typing.ClassVar are properly treated by Pydantic as class variables, 
and will not become fields on model instances:"""      
   
                               
from typing import ClassVar

from pydantic import BaseModel


class Model(BaseModel):
    x: int = 2
    y: ClassVar[int] = 1


m = Model()
print(m) #As we can see, it is not treated as a field of the class. this example only printed the field "x"
#> x=2
print(Model.y) # But if we call it as a variable, then will print.
#> 1                                        










                                ### Private model attributes ###
"""Attributes whose name has a leading underscore are not treated as fields by Pydantic, 
and are not included in the model schema. Instead, these are converted into a "private attribute" 
which is not validated or even set during calls to __init__, model_validate, etc."""

""" __init__ method is overridden to provide custom initialization behavior.
This means that once the class is called, the __init__ configuration is deployed."""

from datetime import datetime
from random import randint

from pydantic import BaseModel, PrivateAttr


class TimeAwareModel(BaseModel):
    _processed_at: datetime = PrivateAttr(default_factory=datetime.now) # default_factory is used with functions
    # or operations to be called, while default is used with static values like int, str, or like that.
    _secret_value: str

    def __init__(self, **data): # __init__ IS THE CONSTRUCTOR, BECAUSE OF THAT, ONCE WE CALL A CLASS TO INSTANCE,
        # IT IS LIKE WE WERE DOING THIS: TimeAwareModel(__init__(_processed_at, _secret_value))
        # IN SUMMARY, WHEN WE CALL __init__ WE'RE RECEIVING THE ATRIBUTES FROM THE INSTANCE, IN THIS CASE
        # EVERY ATRIBUTE, AND THE "**" INDICATES THAT THE INFORMATION IS IN DICTIONARY, OR KEY-VALUE
        # "*" INDICATES, LISTS OR UNITARY VALUES FROM A FOR BUCLE FOR EXAMPLE.
        super().__init__(**data)
        # WE USUALLY USE super().__init__() WITH INHERITATED CLASSES, AND THIS IS A INHERITATED CLASS, BECAUSE WE 
        # INHERITETING FROM Basemodel.
        # this could also be done with default_factory. (that's because randit is a function, NOT a static value)
        self._secret_value = randint(1, 5)

# With __str__() automatically a class prints what we want
# With __repr__() we represent what we want
# With __init__() automatically we get the key-values of the class.(calling them of course)

m = TimeAwareModel()
print(m._processed_at)
#> 2032-01-02 03:04:05.000006
print(m._secret_value)
#> 3









                                        ### DATA CONVERSION ###
"""Pydantic may cast input data to force it to conform to model field types, 
and in some cases this may result in a loss of information."""

from pydantic import BaseModel


class Model(BaseModel):
    a: int
    b: float
    c: str


print(Model(a=3.000, b='2.72', c=b'binary data').model_dump())
#> {'a': 3, 'b': 2.72, 'c': 'binary data'}












                                        ### MODEL SIGNATURE ###
                    
# All Pydantic models will have their signature generated based on their fields:

import inspect

from pydantic import BaseModel, Field


class FooModel(BaseModel):
    id: int
    name: str = None
    description: str = 'Foo'
    apple: int = Field(alias='pear',)


print(inspect.signature(FooModel))
#> (*, id: int, name: str = None, description: str = 'Foo', pear: int) -> None   










                                    ##### FIELD ORDERING #####
# What we've seen right here is that every field is ordered.                                    
"""Field order affects models in the following ways:

field order is preserved in the model schema
field order is preserved in validation errors
field order is preserved by .model_dump() and .model_dump_json() etc."""    


from pydantic import BaseModel, ValidationError


class Model(BaseModel):
    a: int
    b: int = 2
    c: int = 1
    d: int = 0
    e: float


print(Model.model_fields.keys()) # LOOK AT THE SINTAXIS
#> dict_keys(['a', 'b', 'c', 'd', 'e'])
m = Model(e=2, a=1)
print(m.model_dump())
#> {'a': 1, 'b': 2, 'c': 1, 'd': 0, 'e': 2.0}
try:
    Model(a='x', b='x', c='x', d='x', e='x')
except ValidationError as err:
    error_locations = [e['loc'] for e in err.errors()]

print(error_locations)
#> [('a',), ('b',), ('c',), ('d',), ('e',)]








                                        ### REQUIRED FIELDS ####
"""To declare a field as required, you may declare it using just an annotation, or you may use Ellipsis/... 
as the value:"""                                       
# NOTE: This is only a required for 1. versions below. The last versions DO NOT need this.

from pydantic import BaseModel, Field


class Model(BaseModel):
    a: int
    b: int = ...
    c: int = Field(...)








                                    ## MODEL SIGNATURE ##

import inspect ## IT SEEMS THAT inspect HELPS US TO IDENTIFY THE FIELDS IN EXECUTION OF THE OBJECT. 

from pydantic import BaseModel, Field


class FooModel(BaseModel):
    id: int
    name: str = None
    description: str = 'Foo'
    apple: int = Field(alias='pear') # A way to change the key of the attribute


print(inspect.signature(FooModel))
#> (*, id: int, name: str = None, description: str = 'Foo', pear: int) -> None                                
                                    
                                 
# THE SAME inspect BUT WITH A CUSTOM __init__

import inspect

from pydantic import BaseModel


class MyModel(BaseModel):
    id: int
    info: str = 'Foo'

    def __init__(self, id: int = 1, *, bar: str, **data) -> None:
        """My custom init!"""
        super().__init__(id=id, bar=bar, **data)
        ## here we have defined id=id, that means that the key-value in the custom __init__ will be on par with the basemodel
        # __init__, and we defined that through super()(is the one that comunicates the father inherit to the children in 
        # traditional classes). The same happens with bar=bar
        # Making the custom __init__ on par with basemodel __init__ we're been overwriting the second ones.
        # I think **data is getting the extra attributes that were needed.
        # This last one let us write whatever amount of key-values and besides won't help us giving us the key needed. 


print(inspect.signature(MyModel))
#> (id: int = 1, *, bar: str, info: str = 'Foo') -> None 

w = MyModel(1, bar='special', info='format', special='g')                               
print(w)
"""id=1 info='format'"""









                                    #### STRUCTURAL PATTERN MATCHING ######
from pydantic import BaseModel


class Pet(BaseModel):
    name: str
    species: str


a = Pet(name='Bones', species='dog')

match a:
    # match `species` to 'dog', declare and initialize `dog_name`
    case Pet(species='dog', name=dog_name):
        print(f'{dog_name} is a dog')
#> Bones is a dog
    # default case
    case _:
        print('No dog matched')










                                          ###### ATTRIBUTE COPIES #######

from typing import List

from pydantic import BaseModel


class C1:
    arr = []

    def __init__(self, in_arr):
        self.arr = in_arr


class C2(BaseModel):
    arr: List[int]


arr_orig = [1, 9, 10, 3]


c1 = C1(arr_orig)
c2 = C2(arr=arr_orig)
print('id(c1.arr) == id(c2.arr):', id(c1.arr) == id(c2.arr))
#> id(c1.arr) == id(c2.arr): False

print(c1.arr)










                                        ###### EXTRA FIELDS #######

# By default, the extra fields we provide to the instance will just be ignored.
                                        
from pydantic import BaseModel


class Model(BaseModel):
    x: int


m = Model(x=1, y='a')
assert m.model_dump() == {'x': 1}



# But if we want to raise an error we can modify by model_config:

from pydantic import BaseModel, ConfigDict, ValidationError


class Model(BaseModel):
    x: int

    model_config = ConfigDict(extra="forbid")
    # in "extra" field we also have "allow", "ignore" and "forbid"
    # With "ignore" we just ignore the extra attributes and a ValidationError won't raise.
    # But with "forbid" we are raising an error.

try:
    Model(x=1, y='a')
except ValidationError as exc:
    print(exc)
    """
    1 validation error for Model
    y
      Extra inputs are not permitted [type=extra_forbidden, input_value='a', input_type=str]
    """


# We can save the extra fields in __pydantic_extra__

class Model(BaseModel):
    x: int

    model_config = ConfigDict(extra='allow')


m = Model(x=1, y='a')
assert m.__pydantic_extra__ == {'y': 'a'}
print(m.__pydantic_extra__)
"""{'y': 'a'}"""


#By default, no validation will be applied to these extra items, 
# but you can set a type for the values by overriding the type annotation for __pydantic_extra__:

class Model(BaseModel):
    __pydantic_extra__: Dict[str, int]

    x: int 

    model_config = ConfigDict(extra='allow',)


try:
    Model(x=1, y='a')
except ValidationError as exc:
    print(exc)
    """
    1 validation error for Model
    y
      Input should be a valid integer, unable to parse string as an integer [type=int_parsing, input_value='a', input_type=str]
    """

m = Model(x=1, y='2')
assert m.x == 1
assert m.y == 2
assert m.model_dump() == {'x': 1, 'y': 2}
assert m.__pydantic_extra__ == {'y': 2}

g = Model(x=2, y=2)
print(g.model_json_schema())
"""{'additionalProperties': {'type': 'integer'}, 
    'properties': 
        {'x': {'title': 'X', 'type': 'integer'}}, 
    'required': ['x'], 'title': 'Model', 'type': 'object'}"""




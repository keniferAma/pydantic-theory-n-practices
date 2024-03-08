### ejercicios ###


from typing_extensions import Unpack
from pydantic import BaseModel, PositiveInt, ValidationError
from typing import Dict, Optional

from pydantic.config import ConfigDict




class People(BaseModel):
    nombre: str
    apellido: str
    edad: PositiveInt
    activado: bool
    hobbies: Optional[Dict[str, str]] = None


informacion_people = {
    "nombre": "Kenifer",
    "apellido": "Amariles",
    "edad": 30,
    "activado": True,
    "hobbies": {"games": "campo de batalla"}
}

try:
    people_1 = People(**informacion_people)
    print(people_1.model_dump())
    """{'nombre': 'Kenifer', 'apellido': 'Amariles', 'edad': 30, 'activado': True, 'hobbies': {'games': 'campo de batalla'}}"""
    print(people_1.model_json_schema())
    """{'properties': {
            'nombre': {'title': 'Nombre', 'type': 'string'}, 
            'apellido': {'title': 'Apellido', 'type': 'string'}, 
            'edad': {'exclusiveMinimum': 0, 'title': 'Edad', 'type': 'integer'}, 
            'activado': {'title': 'Activado', 'type': 'boolean'}, 
            'hobbies': {
                'anyOf': [
                    {'additionalProperties': {'type': 'string'}, 'type': 'object'}, 
                    {'type': 'null'}
                    ], 
                'default': None, 'title': 'Hobbies'}
                }, 
            'required': [
                'nombre', 'apellido', 'edad','activado'], 
                    'title': 'People', 'type': 'object'
                    }"""
except ValidationError as v:
    print(v)

## En este ejercicio me doy cuenta que model_validate() no fue necesaria para hacer el desempaquetado del diccionario
# y fué basicamente porque cuando vamos a dar argumentos a una instancia en formato Json, es ESTRICTAMENTE necesario}
# usar model_validate(), y cuando lo queremos enviar en formato igual, Json desde afuera en una variable, lo podemos
# hacer mediante desempaquetado.
 
# Pero si pudimos imprimir el resultado esperado mediante model_dump()










# VAMOS A HACER ALGUNAS PRUEBAS DE ANIDACIÓN CON Y SIN ConfigDict:

# Lo que puedo concluir acerca del uso de "model_config = ConfigDict(from_attributes=True)" es el uso para anidar 
# instancias de objetos tradicionales (hechos sin basemodel), en objetos tipo basemodel, con la condición exclusiva
# de que ambos objetos (el de basemodel y tradicional) deben tener los mismos argumentos, correctamente tipados y bien
# definida la configuración model_config = ConfigDict(from_attributes=True) en el objeto "clon" (disponible a anidar)
# y en el objeto anidado.
# NOTA: esto solo podrá ser posible usar mediante la instancia del objeto tradicional, y no anidando dicho objeto 
# a nuestro objeto basemodel.


from pydantic import ConfigDict
from typing import List


class PetCls:
    def __init__(self, *, name: str, specie: str): #COMPROBADO: EL ASTERISCO ES PARA OBLIGARNOS A ESCRIBIR PARAMETRO-VALOR
        self.name = name
        self.specie = specie


class Pet(BaseModel):

    model_config = ConfigDict(from_attributes=True)

    name: str
    specie: str


class Person(BaseModel):

    model_config = ConfigDict(from_attributes=True) #tanto el objeto anidado, como el objeto anidador deben tener
    # model_config

    name: str
    age: int
    pet: Pet


coroso = PetCls(name='coroso', specie='dog') # objeto sin pydantic, debidamente tipado y con los mismos argumentos de "Pet"
murri = PetCls(name='murri', specie='cat')
alonso = Person(name='alonso', age=45, pet=coroso) # en "pet" asignamos la variable del objeto tradicional.








# VAMOS A REALIZAR ALGUNAS PRUEBAS RELACIONADAS CON LAS DIFERENTES MANERAS DE ENVIAR LOS ARGUMENTOS A DICHOS
# OBJETOS.

prueba_parentesis = People(nombre="valquiria", apellido="salamanca", edad=30, activado=True)
# El método mas tradicional, por defecto, pydantic mediante basemodel, nos pide que mencionemos los argumentos
# con sus respectivos valores.

prueba_llaves = People={"nombre": "alonso", "apellido": "fernandez", "edad": 40, "activado": False}
print(prueba_parentesis)
print(prueba_llaves)
"""nombre='valquiria' apellido='salamanca' edad=30 activado=True hobbies=None
{'nombre': 'alonso', 'apellido': 'fernandez', 'edad': 40, 'activado': False}"""
# También podemos observar la manera como se imprime cada opción.
# Podemos concluir que asignando valores mediante llaves es muy parecido a model_validate, sin embargo hay que tener
# en cuenta que cuando usamos model_validate estamos abriendo paréntesis seguido del json, mientras que esta ocación
# lo hemos hecho abriendo directamente las llaves precedidas por "=".










                        ### we are going to practice some generic topics ###

from typing import Generic, TypeVar
from pydantic import BaseModel, SerializeAsAny


class People(BaseModel):
    name: str
    age: int

class Youtuber(People):
    surname: str
    follower_amount: int


T = TypeVar("T", bound=People)

p0 = People(name='antonio', age=23)
p1 = Youtuber(name='fernando', age=70, surname='alcaravan', follower_amount=1234)
p1_model_dumb = p1.model_dump()


class GeneralInfo(BaseModel, Generic[T]):
    info: T
    place: str

p2 = GeneralInfo(info=p1, place='colombia')
print(p2.model_dump())
# This one is the result without model_dumb()
"""info=Youtuber(name='fernando', age=70, surname='alcaravan', follower_amount=1234) place='colombia'"""
# And this one with model_dumb()
"""{'info': {'name': 'fernando', 'age': 70}, 'place': 'colombia'}"""
### AS WE EXPECTED, IT GETS THE FIELDS OF THE CLASS IN WITCH WAS BOUNDED, IT MEANS "People" CLASS
# But as something curious was that without model_dumb, it printed everything.
# Besides, the extra fields we sent to "GeneralInfo" does not generate an error.


# Now we are gonna try to generate an error by sending wrong values:

J = TypeVar("J", bound=Youtuber)

class GeneralInfo(BaseModel, Generic[J]):
    info: J
    place: str
    
# p3 = GeneralInfo(info=People(name='alejandro', age=23), place='colombia')
# print(p3.model_dump())
"""Input should be a valid dictionary or instance of Youtuber [type=model_type, input_value=People(name='alejandro', age=23), input_type=People] 
    For further information visit https://errors.pydantic.dev/2.0.3/v/model_type"""
### IT IS NOT POSIBLE SETTING LESS FIELDS THAN THE "Generic", WITH "TypeVar", ASKS.

p3 = GeneralInfo(info=p1, place='colombia')
print(p3.model_dump())
### THIS ONE IS CORRECT.


### PROVING THE SAME PROCESS BUT WITHOUT generic models:

class People(BaseModel):
    name: str
    age: int
    

class Youtuber(People):
    surname: str
    follower_amount: int

class GeneralInfo(BaseModel):
    info: People
    place: str


p6 = People(name='antonio', age=23)
p5 = Youtuber(name='oswald', age=21, surname='alarcon', follower_amount=2)
p4 = GeneralInfo(info=p5, place='argentina')
print(p4.model_dump())
"""Input should be a valid dictionary or instance of Youtuber [type=model_type, input_value=People(name='antonio', age=23), input_type=People]   
    For further information visit https://errors.pydantic.dev/2.0.3/v/model_type"""
# WITH TRADITIONAL CLASSES, IT IS NOT POSIBLE TO SET LESS FIELDS THAN THE REQUIRED, IT IS THE SAME AS generic 
# AT THIS ASPECT.

# BUT IT IS ALSO POSIBLE AS generic, SETTING MORE FIELDS THAN THE REQUIRED.
# IN SUMMARY, THE BEHAVIOR BETWEEN BOTH "Generic" and "tradicional" classes are the SAME

p7 = People.model_validate({'name': 'abelardo', 'age': 2})
# p7 = People.model_validate('carlos', 30) # it is not posible sending non-dict values in model_validate.







# WE ARE GOING TO PRACTICE SOME PrivateAtr EXERCISES
from dataclasses import dataclass
from pydantic import PrivateAttr
import datetime

## IT SEEMS THAT WITH PYDANTIC ONCE YOU SET "_" BEFORE ANY FIELD KEY, IT'S TAKEN AS PRIVATE VALUE.
class PrivateA(BaseModel):
    name: str 
    _surname: str
    _age: int
    _password: int 


private_person = PrivateA(name='abelardo')
print(private_person)
"""name='abelardo'"""




class PrivateB(BaseModel):
    _name: int = PrivateAttr(default=123) # with static values we use default.
    surname: str
    age: int
    password: int

    def __init__(self, **data):
        super().__init__(**data)
        self.age = 2

p = PrivateB(surname="jaramillo", age=23, password=123)
print(p)
"""surname='jaramillo' age=2 password=123"""
# We changed the "age" field through __init__(), witch, in summary is receiving the same dictionary information.


class PrivateC(BaseModel):
    lista: List[str]


ajam = PrivateC(lista=['manuel', 'alejandro', 'fidel'])
print(ajam)











#### MORE PRACTICES WITH model_config, ConfigDict AND THIS TIME dataclasses.
# IN SUMMARY WE CAN DEFINE THAT WITH DATACLASSES THIS ESTRUCTURE WORKS THE SAME AS TRADITIONAL CLASSES.
from pydantic import ConfigDict
from typing import List
from dataclasses import dataclass


@dataclass
class PetData:
    name: str
    specie: str
    age: int



class PetCls:
    def __init__(self, *, name: str, specie: str, age: int):
        self.name = name
        self.specie = specie
        self.age = age


class Pet(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str
    specie: str
    age: int


class Person(BaseModel):

    name: str
    age: int
    pet: Pet


tony = PetData('tony', 'dog', 3)
coroso = PetCls(name='coroso', specie='dog', age=4) 
murri = PetCls(name='murri', specie='cat', age=4)
alonso = Person(name='alonso', age=45, pet=coroso) 
pedro = Person(name='pedro', age=23, pet=tony) 

print(alonso.model_dump())





                                        


                             ### SOME TypeVar EXERCISES ###
# Let's make some exercises with TypeVar and Generic

from typing import Generic, TypeVar

Hamburguer = TypeVar('Hamburguer') # of course we can set this field "bound=str" or whatever.


class Food(BaseModel, Generic[Hamburguer]):
    real_food: str
    mexican_food: str
    taxes: int
    fast_food: Hamburguer

client = Food[str](real_food="solomito", mexican_food="burrito", taxes= 23, fast_food="cheese")
# When we don't bound the type inside "TypeVar" we must do it after calling the instance among brackets.
# Even if we have fields set as "int", the type between the brackets will only afect the typevar value.
# psd: we made the probe setting "fast_food" as "int" and it generates an error.











                                    # SOME Field_validator EXCERCISES #

from pydantic import field_validator, create_model
from model_exercises_functions import function_to_validator # we set the function in another carpet.


Field_validator_dict = {'age_validator': field_validator('age')(function_to_validator)}      

# making some probes with basemodel classes.
class Lawyer(BaseModel):
    name: str
    surname: str
    age: int
    __pydantic_validator__=Field_validator_dict
    # as we can see, it is not possible to set the same __validators__ as with created_model
    # maybe this will be posible with some decorator or like that.


l = Lawyer(name='nestor', surname='martinez', age=23) # It is not working properly with basemodel classes.


# making some probes with create_model

LawyerCreated = create_model(
    'LawyerCreated',
    name=(str, ...),
    surname=(str, 'fernandez'),
    age=(int, ...),
    __validators__=Field_validator_dict # we set the validator function on this field, inside the model.
)

m = LawyerCreated(name='alberto', age=5) 
print(m.model_dump())








### PRACTICING SOME ITERATION AND MORE WITH RootModel
from pydantic import RootModel


class Tools(RootModel):
    root: List[str] # MUST BE WITH "root", ONLY WITH THAT.

    def __iter__(self):
        return iter(self.root)

    def __getitem__(self, item):
        return self.root[item]

j = Tools(root=['hammer', 'claws', 'screws'])
print([l for l in j])
print(j[2])


# PROBING WETHER WE CAN CREAT AN INSTANCE WITH A LIST WITHOUT UNPACKING OR NOT.

class Without(BaseModel):
    elements: List[str]

lista = ['a', 'b', 'c']
w = Without(elements=lista)

print(w)








                               ### RootModel ### MORE EXCERCISES ###

from pydantic import RootModel

class Traditional(RootModel):
    root: str # "root" IS ONLY ALLOWED


j = Traditional(root='debate')
print(j.root)


class Desition(RootModel[Dict[str, str]]): #Even if we set this way, root is the root.
    pass ### we set pass, because RootModel only accepts 1 element.

    def __iter__(self): #Whatever function that iterates this class, will automatically call this method.
        iter(self.root)

m = Desition(root={'medellin': 'antioquia'})
print(m.root) 











## EXERCISING model_construct : THERE WERE NO DIFFERENCE WITH AND WITHOUT IT.
class Construct(BaseModel):
    name: str 
    surname: str

s = Construct(name="carlos", surname="fernando")
model = s.model_dump()
f = Construct(**model)
print(f)








#SOME EXERCISES WITH PrivateAttr AND __init__

class Animals(BaseModel):
    tipe: str 


class Unknown(BaseModel):
    tipe: str="tomillo"


class Horse(Animals):
    _name: str = PrivateAttr(default="COLOSO")
    _age: int
    _otro: Unknown = PrivateAttr(default_factory=Unknown)

    def __init__(self, **data): ## THIS IS ONLY TO SET A DEFAULT VALUE TO PRIVATE FIELDS.
        super().__init__(**data)
        self._age = 12

    def show(self):
        return f"{self._age}"
    
    def receive(self, *, age):
        self._age = age

    def show_name(self):
        return self._name
    
    def show_unknow(self):
        return self._otro
    

bella = Horse(tipe='horse', _name='bella') # IT'S NOT POSSIBLE ASSIGN ANY VALUE TO PRIVATE ATRIBUTES.
print(bella.model_dump())
print(bella.show()) ## AS IN REGULAR PRIVATE FIELDS, A WAY TO REPRESENT THE PRIVATE VALUE, WITH A METHOD.
"""12"""

bella.receive(age=10)
print(bella.show()) ## BY A METHOD, THE PRIVATE FIELD WAS CHANGED.
"""10"""

print(bella.show_name())
"""COLOSO"""

print(bella.show_unknow())












                                                #EXERCISING __init__

class Initializer(BaseModel):
    key: str

    def __init__(self, **data):
        super().__init__(**data)
        self.key = "fresa"


i = Initializer(key= 'balon')
print(i)



class Init(BaseModel):
    _primero: str
    segundo: str

    def __init__(self, **data):
        super().__init__(**data)
        self._primero: str = 'carlos'


l = Init(primero='blanco', segundo='azul', tercero='gris')
print(l.model_dump())

## SOMETHING TO SUMMARIZE:
# 1 when we set more than the expected fields, this object accepts it. but only represents the ones that are not private.
# 2 **data allows us to set the atributes Key-value as we want.


class InitRecreation(BaseModel):
    primero: str
    segundo: str

    def __init__(self, tercero: str, **data):
        super().__init__(tercero=tercero, **data) ## **data won't help me setting the key-values in the instance(only basemodel attributes)
        # so I'll have to keep them in mind. We are allowing the class to give us infinite key-values elements.
        # And with "tercero", which is the one that is not in the basemodel __init__, we have to comunicate it with the
        # the basemodel __init__, to make the entire fields work.


#KEEP IN MIND: super() IS WORKING AS ALWAYS; COMUNICATING THE FATHER WITH THE CHILD. ON THIS CASE, THE CUSTOM __init__
#WITH THE FATHER WHICH IS basemodel WITH THE ATTRIBUTES primero AND segundo.
r = InitRecreation(primero='caballo',cuarto='gato', tercero="claro", segundo="perro")
print(r)
    

class Init(BaseModel):
    primero: str
    segundo: str

h = Init(primero='string', segundo='integrate', tercero='booleano') ## WITH REGULAR WE CAN ALSO GIVE INFINITE key-values ELEMENTS.
print(h) ### BUT LESS THAN THE REQUIRED IS NOT POSSIBLE.


### WITHOUT "**data" IN REGULAR basemodel FUNCTIONS WE CAN SEND AS MANY ELEMENTS AS WE WANT.
class MyModel(BaseModel):
    id: int
    info: str = 'Foo'

    # def __init__(self, id: int = 1, *, bar: str, **data) -> None:
    #     """My custom init!"""      
    #     super().__init__(id=id, bar=bar, **data)
         
# SUMMARIZING: WITH TRADITIONAL basemodel FUNCTIONS, WE CAN SEND AS MANY ARGUMENTOS TO THE INSTANCE AS WE WANT
# BUT IN ORDER TO HAVE THE SAME EFFECT IN THE CUSTOM __init__, WE'RE GONNA HAVE TO SET **(something).
# DOING IT THAT WAY WE'RE FAVORING THE CUSTOM __inti__ ATTRIBUTES RATHER THAN THE ORIGINAL basemodel ONES.
# THA'S THE REASON WE HAVE NO THE keys AS HELP OF THE basemodel
# WHEN WE SET A __init__ METHOD WE ONLY HAVE 


w = MyModel(id=1, bar='special', info='format', special='g')                               
print(w)
"""id=1 info='format'"""


### PROBING __init__ ATTRIBUTES ONLY:
## RESULT: WE MUST SET **data

class OnlyInit(BaseModel):
    name: str
    surname: str
    age: int
    def __init__(self, age: int, **data):
        super().__init__(age=age, **data)
        

try:
    v = OnlyInit(age=32, name='alberto', surname='uribe')
    print(v.model_dump())

except ValidationError as e:
    print(e.json())









                                                # Identifiquer (id)

class Copy1:
    value = []

    def __init__(self, v):
        self.value = v


class Copy2:
    value = []

    def __init__(self, v) -> None:
        self.value = v


class Copy3(BaseModel):
    value: List[int]


lista = [1, 2, 3, 4, 5, 6]

c1 = Copy1(lista) # To remember, with regular classes we don't have to set the "key" of the argument.
c2 = Copy2(lista)
c3 = Copy3(value=lista)

print(id(c1.value))
"""2008018836672"""
print(id(c2.value))
"""2008018836672""" # memory id are the same in regular classes with the same attribute.
print(id(c3.value))
"""2527900649984""" ## As we can see, with the same element as attribute, 
                    ## the basemodel attributes go to another memory id.






class Prica(BaseModel):
    model_config = ConfigDict(extra="allow")

    name: str
    _surname: str = PrivateAttr(default="Hernandez")


h = Prica(name="carlos", extra="fercho")
print(h.model_dump())
print(h._surname)
print(h.__pydantic_extra__) # The only way we could print this was by setting model_config, ConfigDict, extra.








## let's prove some List vs Sequence validations ##
from typing import Sequence


class Sque(BaseModel):
    itera_sequence: Sequence[int]
    itera_list: List[int]


d = Sque(itera_sequence=(1,2,3,4), itera_list=(1,2,3,4))




print(d.model_dump())


# CODE FROM AI BING:
# DID NOT GIVE ME A EXPLANATION. (FAIL)
# WE DO NOT KNOW THE REAL DIFFERENCES BETWEEN BOTH TYPES List AND Sequence YET.
# I THINK IT IS JUST TO TYPE MATTER
from typing import List, Sequence
from pydantic import BaseModel

class ModelList(BaseModel):
    numbers: List[int]

class ModelSequence(BaseModel):
    numbers: Sequence[int]

# Esto funcionará
print(ModelList(numbers=[1, 2, 3]))
print(ModelSequence(numbers=[1, 2, 3]))
print(ModelSequence(numbers=(1, 2, 3)))
print(ModelList(numbers=(1, 2, 3)))

# Esto generará un error (FAIL)
try:
    print(ModelList(numbers=(1, 2, 3)))
except Exception as e:
    print(e)



from pydantic import field_validator
from pydantic.dataclasses import dataclass


@dataclass
class DemoDataclass:
    product_id: str  # should be a five-digit string, may have leading zeros.
    # As we know without basemodel we can't parse the type at the beginning. so withc only dataclass we can not parse 
    # the atributes types.
    @field_validator('product_id', mode='before')
    @classmethod
    def convert_int_serial(cls, v):
        if isinstance(v, int):
            v = str(v).zfill(5)
        return v


print(DemoDataclass(product_id='01234'))
#> DemoDataclass(product_id='01234')
print(DemoDataclass(product_id=2468))
#> DemoDataclass(product_id='02468')



#### Some @field_validator and concepts about FieldValidationInfo ####
## When we set an argument in methods with the decorator "@field_validator" as "FieldValidationInfo" we are getting
# more information about the exact error we got, such as the field that caused the error

from pydantic import (
    BaseModel,
    FieldValidationInfo,
    ValidationError,
    field_validator,
)


class UserModel(BaseModel):
    id: int
    name: str

    @field_validator('name')
    @classmethod
    def name_must_contain_space(cls, v: str) -> str:
        if ' ' not in v:
            raise ValueError('must contain a space')
        return v.title()

    # you can select multiple fields, or use '*' to select all fields
    @field_validator('id', 'name')
    @classmethod
    # REMEMBER: First value is the "cls", second is the value (we can name it as we want)
    # and third if we want is FiedValidationInfo
    def check_alphanumeric(cls, v: str, info: FieldValidationInfo) -> str:
        if isinstance(v, str):
            # info.field_name is the name of the field being validated
            is_alphanumeric = v.replace(' ', '').isalnum()
            assert is_alphanumeric, f'{info.field_name} must be alphanumeric'
        return v


print(UserModel(id=1, name='John Doe'))
#> id=1 name='John Doe'

try:
    UserModel(id=1, name='samuel')
except ValidationError as e:
    print(e)
    """
    1 validation error for UserModel
    name
      Value error, must contain a space [type=value_error, input_value='samuel', input_type=str]
    """

try:
    UserModel(id='abc', name='John Doe')
except ValidationError as e:
    print(e)
    """
    1 validation error for UserModel
    id
      Input should be a valid integer, unable to parse string as an integer [type=int_parsing, input_value='abc', input_type=str]
    """

try:
    UserModel(id=1, name='John Doe!')
except ValidationError as e:
    print(e)
    """
    1 validation error for UserModel
    name
      Assertion failed, name must be alphanumeric
    assert False [type=assertion_error, input_value='John Doe!', input_type=str]
    """





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



from typing import Any

from pydantic import BaseModel, ValidationError, model_validator


class UserModel(BaseModel):
    username: str
    password1: str
    password2: str

    @model_validator(mode='before')
    @classmethod
    def check_card_number_omitted(cls, data: Any) -> Any:
        if isinstance(data, dict):
            assert (
                'card_number' not in data
            ), 'card_number should not be included'
        return data

    @model_validator(mode='after')
    def check_passwords_match(self) -> 'UserModel':
        pw1 = self.password1
        pw2 = self.password2
        if pw1 is not None and pw2 is not None and pw1 != pw2:
            raise ValueError('passwords do not match')
        return self


print(UserModel(username='scolvin', password1='zxcvbn', password2='zxcvbn'))
#> username='scolvin' password1='zxcvbn' password2='zxcvbn'
try:
    UserModel(username='scolvin', password1='zxcvbn', password2='zxcvbn2')
except ValidationError as e:
    print(e)
    """
    1 validation error for UserModel
      Value error, passwords do not match [type=value_error, input_value={'username': 'scolvin', '... 'password2': 'zxcvbn2'}, input_type=dict]
    """

try:
    UserModel(
        username='scolvin',
        password1='zxcvbn',
        password2='zxcvbn',
        card_number='1234',
    )
except ValidationError as e:
    print(e)
    """
    1 validation error for UserModel
      Assertion failed, card_number should not be included
    assert 'card_number' not in {'card_number': '1234', 'password1': 'zxcvbn', 'password2': 'zxcvbn', 'username': 'scolvin'} [type=assertion_error, input_value={'username': 'scolvin', '..., 'card_number': '1234'}, input_type=dict]
    """




# some SkipValidation concepts #

from typing import List

from pydantic import BaseModel, SkipValidation


class Model(BaseModel):
    names: List[SkipValidation[str]]


m = Model(names=['foo', 'bar'])
print(m)
#> names=['foo', 'bar']

m = Model(names=['foo', 123])  
print(m)
#> names=['foo', 123]



# vamos a realizar algunos ejercicios relacionados con los decoradores @field_validator y @model_validator:

from pydantic import field_validator, ValidationError, BaseModel
from typing import Optional

class FieldValidator(BaseModel):
    name: str
    surname: str
    age: int
    address: Optional[str] = None

    @field_validator("name", "surname")
    @classmethod
    def validando(cls, v: str):
        if v[0] != "a":
            raise ValueError("The name doesn't start with 'a'")
        else:
            return v.title()
# Importante tener en cuenta:
"""Cuando utilizas el decorador @field_validator, Pydantic captura cualquier ValueError o TypeError 
que se lance y los convierte en un ValidationError. Esto permite que Pydantic maneje todos los errores 
de validación de manera coherente y proporcione mensajes de error útiles."""
## ES DECIR, "ValidationError" SE USA SOLA Y EXCLUSIVAMENTE CON LA INSTANCIA DE LA CLASE EN PYDANTIC. Pienso que
# puede ser debido a su configuración interna del manejo de dichos errores, es decir, está elaborado con errores
# de clase.
    
try:
    print(FieldValidator(name="alejandro", surname="amariles", age=30).model_dump())

except ValidationError as e:
    print(e)


class VerifyAge(BaseModel):
    name: str
    age: int

    @field_validator("age")
    @classmethod # Para recordar que en pydantic los métodos de clase se ejecutan automaticamente.
    def older(cls, value: int):
        if value < 18:
            raise ValueError("You are under age")
        return value
    
try:
    alberto = VerifyAge(name="Alberto", age=32)
    print(alberto.model_dump())

except ValidationError as message:
    print(message)



import re
from pydantic import Field
from typing import List
from fastapi import HTTPException

class EmailValidator(BaseModel):
    name: str = Field(default="Bernardo")
    age: int
    hobbies: list[str] = Field(default=["playing", "going out"])
    email: str

    @field_validator("email")
    @classmethod
    def email_validator(cls, value: str):
        pattern = r"[a-zA-Z0-9]@gmail.com|@hotmail.com"
        result = re.findall(pattern, value)
        if not result:
            raise ValueError("Invalid email")
        return value
    
try:
    alejandro = EmailValidator(name="alejandor", age=30, email="alejandro34@hotmail.com")
    print(alejandro.model_dump())

except ValidationError as message:
    print(message)



# Ahora vamos a intentar validar una mayoria de edad y además que sea positivo.

from pydantic import PositiveInt

class OlderNPositive(BaseModel):
    name: str
    age: PositiveInt # Como podemos observar no es necesario asignar un validador para numeros positivos.
    email: str

    @field_validator("age")
    @classmethod
    def age_validator(cls, value: int):
        if value < 18:
            raise ValueError("You must be over 18")
        return value


try: 
    Fidel = OlderNPositive(name="fidel", age=21, email="fidel@gmail.com")
    print(Fidel.model_dump())

except ValidationError as message:
    print(message)




# Now we're gonna try to verify the times of field_validators (Before, After, Plain):

class TimesProof(BaseModel):

    name: str
    surname: str
    age: PositiveInt

    @field_validator("age", mode="before")#Proved with "before", in efect by doing before validates the classmethod
    @classmethod
    def age_older(cls, age):
        if age < 18:
            raise ValueError("You have to be older")
        return age
    
try:
    Bernardo = TimesProof(name="Bernardo", surname="Velasquez", age=-3)
    print(Bernardo.model_dump())

except ValidationError as message:
    print(message)




# Let's make some exercises to practice field_validator and FieldValidationInfo. Also ValidatioError.

from pydantic import (
    BaseModel,
    field_validator,
    FieldValidationInfo,
    ValidationError, 
    Field,
    PrivateAttr,

)
from typing import List
import re

class ExerciseWithFieldValidationInfo(BaseModel):
    name: str 
    age: int
    hobbies: List[str]
    email: str 


    """Validating the minimun amount of hobbies"""
    @field_validator("hobbies")
    @classmethod
    def hobbies_validator(cls, value: List, aditional_info: FieldValidationInfo):
        if len(value) < 2:
            raise ValueError(f"{aditional_info.field_name} must have at least 3 hobbies.")
        
        return value
    

    """Validating there is not numbers in the name"""
    @field_validator("name")
    @classmethod
    def name_validator(cls, value: str):
        pattern = r"[a-zA-Z]{1,}"
        result = re.findall(pattern, value)

        if len(value) < 1:
            raise ValueError("Name must have more than 1 word")
        
        if len(value) != len(result[0]):
            raise ValueError("Name must have only words")
        
        return value
    
    
    """Validating age based on over age"""
    @field_validator("age")
    @classmethod
    def age_validator(cls, value: int):
        if value < 18:
            raise ValueError("You must be over 18 years old")
        
        return value



try:
    samuel = ExerciseWithFieldValidationInfo(
    name="samuel",
    age=19,
    hobbies=["platino", "going hiking", "swimming", "camping", "porning"],
    email="samuel@gmail.com"
)
    print(samuel.model_dump())

except ValidationError as message:
    print(message)




###### model_validator exercises #####

from pydantic import BaseModel, model_validator, ValidationError, Field
import random
import string

def random_passwords() -> str:
    password = random.choices(string.ascii_lowercase, k=5)
    return "".join(password)


class PasswordCheck(BaseModel):
    name: str 
    password1: str = Field(default=random_passwords())
    password2: str
    expiration: int

    @field_validator("password1", "password2")
    @classmethod
    def password_length(cls, value: str, more_info: FieldValidationInfo): 
        if len(value) < 5:
            raise ValueError(f"The {more_info.field_name} length must be longer than 5")
        return value
    
    @model_validator(mode="after") # No estamos usando un método de clase para after debido a que se activa una vez
    # la instancia está creada y por consiguiente ya tenemos nuestra validación hecha por basemodel, es decir
    # que ya tenemos a nuestra disposición todos los campos, por ello simplemente usamos self como nuestro argumento
    # y desde aquí simplemente llamamos a los campos que deseamos intervenir. CASO CONTRARIO pasa cuando usamos modo=before
    # ya que aún no tenemos un modelo validado por pydantic y por consiguiente no tenemos una instancia. En este caso
    # debemos usar métodos de clase que se ejecutan directamente desde la clase y no desde una instancia. 
    # Para recordar que cuando usamos métodos de clase con model_validator ya que usamos métodos de clase, el primer 
    # argumento es bien sabido que es "cls", el segundo nuestro valor (podemos dar cualquier valor) y ya si queremos
    # dar un tercer argumento entonces lo podemos hacer con FieldValidationInfo, el cual usamos para obtener información 
    # adicional como el nombre del campo que nos falla durante la validación, y otros más que obtenemos una vez instanciamos
    # dicha función de información adicional.
    def cheking_passwords_match(self) -> "PasswordCheck":
        psw1 = self.password1
        psw2 = self.password2

        if psw1 is not None and psw2 is not None and psw1 != psw2:
            raise ValueError("The passwords do not match")
        return self
    
try:
    ramiro = PasswordCheck(name="Ramiro", password2="xyztg", expiration=12)
    print(ramiro)

except ValidationError as message:
    print(message)


# let's try to practic PydanticCustomError

from pydantic_core import PydanticCustomError

class CustomErrorPractice(BaseModel):
    name: str
    surname: str
    age: int

    @model_validator(mode="after")
    def length_of_strings(self, values) -> "CustomErrorPractice":
        name_length = self.name
        surname_length = self.surname

        if len(name_length) < 1 or len(surname_length) < 1:
            raise PydanticCustomError(
                "length error",
                "{name} and {surname} is the answer",
                {"number": values, "surname": values}
                
            )
        return self

try:
    jose = CustomErrorPractice(name="", surname="hortua", age=23)
    print(jose)

except ValidationError as message:
    print(message)





# proves with field_validator and classmethod:

class CustomError(BaseModel):
    age: int

    @field_validator("age")
    @classmethod
    def length_of_strings(cls, values) -> int:
        if values < 18:
            raise PydanticCustomError(
                "age error",
                "{age} must be older", # the name between braces must be the same field name we are parsing. 
                {"age": values}
            )
        
        return values
try:
    albertino = CustomError(age=12)
    print(albertino)

except ValidationError as message:
    print(message)

# One conclusion we can define on this two PydanticCustomError exercises is that we only got the result we wanted
# with "field_validator" instead of "model_validator", besides we used a classmodel decorator to make this last one exercise 
# works correctly. or aparently does not work with several fields at the same time.






### SkipValidation practices, but this time with pydantic validation ###
from pydantic import SkipValidation

class Skip(BaseModel):
    name: SkipValidation[str] # HERE we set to SKIP the name field parsing, so we can give whatever type of data as argument.
    surname: str
    hobbies: List[SkipValidation[str]] # AND here happens the same with hobbies field.

try:
    jose = Skip(name=1, surname="alarcon", hobbies=["playing soccer", 12])
    print(jose)
except ValidationError as message:
    print(message)






#### SkipValidation practices ####
#### But went wrong because we realized that basic oriented object programation doesn't parse information ####

from pydantic import InstanceOf

class Person:
    def __init__(self, name: str, surname: str, age: int) -> None:
        self.name = name 
        self.surname = surname
        self.age = age


class Employee(Person):
    def __init__(self, name: str, surname: str, age: int, role: str) -> None:
        super().__init__(name, surname, age)

        self.role = role

    def __repr__(self) -> str:
        return f"{self.name}"


alfredo = Employee(12, "amariles", 21, "electrician")
print(alfredo)





#### some InstanceOf practices ####

from dataclasses import dataclass
from pydantic import InstanceOf

@dataclass
class Person:
    name: str
    surname: str
    age: int


@dataclass
class Employee(Person):
    role: List[str]


@dataclass
class Strange:
    name: str
    surname: str


class Personal(BaseModel):
    illness: InstanceOf[Person]



carlos = Employee("carlos", "velez", 76, ["soccer", "walking"])

fernando = Strange("fernando", "hernandez")

try:
    kayden = Personal(illness=fernando) # Giving instance from another class.
    print(kayden)

except ValidationError as message:
    print(message)

"""Input should be an instance of Person [type=is_instance_of, input_value=Strange(name='fernando', surname='hernandez'), input_type=Strange] 
    For further information visit https://errors.pydantic.dev/2.1/v/is_instance_of"""

## PROVED ##




#### pydantic.dataclasses ####

from pydantic.dataclasses import dataclass


@dataclass
class DataclassProve:
    name: str
    surname: str
    age: int

    @field_validator("age", mode="before")
    @classmethod
    def multipling_age(cls, value):
        if isinstance(value, int):
            return value * 2
        
        return value
        

amparo = DataclassProve("amparo", "ceron", "44") # field_validator is acting like it had a basemodel, I mean, it parses the type in
# before like it was with basemodel.
print(amparo)
        

from pydantic_core import PydanticCustomError

from pydantic import BaseModel, ValidationError, field_validator


class Model(BaseModel):
    x: int

    @field_validator('x')
    @classmethod
    def validate_x(cls, v: int) -> int:
        if v % 42 == 0:
            raise PydanticCustomError(
                'the_answer_error',
                '{number} is the answer!',
                {'number': v},
            )
        return v


try:
    Model(x=42 * 2)
except ValidationError as e:
    print(e)
    """
    1 validation error for Model
    x
      84 is the answer! [type=the_answer_error, input_value=84, input_type=int]
    """



class OptionalClass(BaseModel):
    id: Optional[int] = Field(default=None)
    name: str


persona_optional = OptionalClass(name='alejandro')
print(persona_optional)
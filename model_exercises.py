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














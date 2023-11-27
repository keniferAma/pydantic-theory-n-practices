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


import json
from pydantic import BaseModel, field_validator, InstanceOf
from typing import List, Optional




class MayoresEdadError(Exception):
    def __init__(self, value, message) -> None:
        self.value = value
        self.message = message

        super().__init__(message)


class PersonasJson(BaseModel):
    nombre: str
    apellido: str
    edad: int
    estado_civil: str
    ciudad_de_residencia: str
    sexo: str
    hobbies: Optional[list[str]]
    modificaciones_corporales: bool

    @field_validator("edad")
    @classmethod
    def mayores_de_edad(cls, value) -> None:
        if value < 18:
            raise MayoresEdadError(value=value, message="Legal age only.")
        
        return value
        


path = "c:/Users/kenifer/Desktop/pruebas-json/personas.json"

with open(path) as file:
    data = json.load(file)
    

try:
    informacion_global: List[InstanceOf[PersonasJson]] = [PersonasJson(**item) for item in data]
    print(informacion_global)

except MayoresEdadError as message:
    print(dict(message))



def selector(nombre: str):
    for i, x in enumerate(informacion_global):
        if x.nombre == nombre:
            return informacion_global[i]
    
    raise MayoresEdadError(value=nombre, message="No fue posible encontrar")



try:
    print(selector("guillermo"))

except MayoresEdadError as m:
    print(f'{m.message} a {m.value}')
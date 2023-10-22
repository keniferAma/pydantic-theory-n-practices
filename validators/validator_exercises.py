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


## some model_dump exercises ###
from pydantic import Field, BaseModel, ValidationError, PositiveInt 
from typing import Optional, Literal



class DumpSerialization(BaseModel):
    name: str
    surname: Optional[str] = 'Carmona'
    age: PositiveInt
    email: str 


user = DumpSerialization(name='Amanda', age=12, email='Amanda@gmail.com')

print(user.model_dump(exclude_defaults=True)) # As 'surname' is set by default with 'Carmona', it's not serialized.
"""{'name': 'Amanda', 'age': 12, 'email': 'Amanda@gmail.com'}"""



from enum import Enum

class Ensayo(BaseModel, Enum):
    nombre: str
    apellido: str


carlos = Ensayo(nombre='carlos', apellido='gurrimbo')
print()
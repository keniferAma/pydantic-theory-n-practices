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






# User registation: challenge suggested by artificial inteligence #

import re
import json
from datetime import date, timedelta, datetime

user_registation_path = 'C:/Users/kenifer/Desktop/pruebas-json/english-database.json'


"""
To remember, implementing a file error handling is a good practice, specially when it is developes outside
of the classes. when inside, it is also a good practice implementing a try-except error due to the extra information
we can get from the python warnings. Also remember that we're using """
try:
    with open(user_registation_path) as user_registation_file:
        information = json.load(user_registation_file)

except FileNotFoundError:
    print(f'The file {user_registation_path} did not work.')

except PermissionError:
    print(f"Permission denied when trying to open the file {user_registation_path}")

except json.JSONDecodeError:
    print(f'The file {user_registation_path} does not contain a valid JSON.')


# Remember that we're printing the exception outputs, even though we should implement 'raise' errors due to 
# the severity of not finding a file. This also applies when the json loader or file reader is inside the class 
# (usually implemented when the file is too large).



class UserRegistrationError(Exception):
    """Making a custom validation error handler for this challenge"""
    def __init__(self, message=None, value=None) -> None:
        self.value = value
        self.message = message


class UserRegistation(BaseModel):
    username: str
    password: str
    email: str
    date_of_birth: str

    @field_validator('username')
    @classmethod
    def username_validator(cls, value):        
        username_pattern = r'[a-z0-9_]{1,}'
        result_regular = re.match(username_pattern, value)

        if not result_regular:
            raise UserRegistrationError(message={'Username_error': 'only allowed lowercase and underscore.'})
                                        
        start, end = result_regular.span()

        if value != value[start: end]:
            raise UserRegistrationError(message={'Username_error': 'only allowed lowercase and underscore.'})
        
        if len(value) < 3 or len(value) > 30:
            raise UserRegistrationError(message={'Username_error': 'max lenght between 3-30 characters only.'})
        
        return value


    @field_validator('password')
    @classmethod
    def password_validation(cls, value):
        """making a password validation entrance"""
        if len(value) <= 8:
            raise UserRegistrationError(message={'Password_error': 'The password must have at least 8 characters.'})
        
        password_pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).+$' # REMEMBER THAT "=?" ALLOWS US TO SEARCH
        # WITHOUT SPENDING CHARACTERS, WHICH IS GOOD FOR THIS PURPOSE.
        # We also remeber that the dot '.' means whatever character and the asterisc '*' means that character
        # must be 0 or more and before the following character which are [a-z], [A-Z] and '\d'.

        result_for_regular = re.search(password_pattern, value)
        if not result_for_regular:
            raise UserRegistrationError(value=value, 
                                        message={'Password_error': 'the password does not fit the requirement.'})
        
        start, end = result_for_regular.span()
        if value != value[start: end]:
            raise UserRegistrationError(value=value, 
                                        message={'Password_error': 'the password does not fit the requirement.'})

        return value
    
    
    @field_validator('email')
    @classmethod
    def email_validator(cls, value):
        """making a validator to check if the email is indeed a email"""

        email_pattern =  r'^[a-zA-Z0-9_]{5,}@[a-z]{5,}(?:\.(?:edu|com))?\.(?:com|es|co)$'
        pattern_result = re.findall(email_pattern, value)

        if not pattern_result:
            raise UserRegistrationError(message={'email_error': 'the email does not match the requirements.'})
        
        if len(pattern_result[0]) != len(value):
            raise UserRegistrationError(message={'email_error': 'the email does not match the requirements.'})

        return value
    

    @field_validator('date_of_birth')
    @classmethod
    def date_of_birth_validator(cls, value):
        """making a validator to chek date_of_birth"""
        date_of_birth_pattern = r'^[0-9]{4}(-|/)[0-9]{1,2}(-|/)[0-9]{1,2}$'
        result_regular = re.findall(date_of_birth_pattern, value)

        if not result_regular:
            raise UserRegistrationError({'date_error': 'the date is invalid.'})

        
        actual_date = date.today()
        actual_day = actual_date.day
        actual_month = actual_date.month
        actual_year = actual_date.year

        age_mayority = (datetime(day=actual_day, month=actual_month, year=actual_year) - 
                        datetime(year=int(value[:4]), month=int(value[5:7]), day=int(value[8:10])))
                                                                                                 

        if age_mayority.days < 6575:
            raise UserRegistrationError({'date_error': 'You must be older than 18'})
        
        return value
    

try:
    general_information: List[UserRegistation] = [UserRegistation(**item) for item in information['users']]
    
                                       
except UserRegistrationError as msj:
    print(msj.message)
    



# SOME NOTATIONS RELATED WITH REGULAR EXPRESSIONS #
pattern_to_practice = r'^[a-zA-Z0-9_]{5,}@[a-z]{5,}(?:\.(?:edu|com))?\.(?:com|es|co)$'
"""IMPORTANT
WHEN WE USE 'findall', THIS FEATURE HAS LIKE A 'PRIORITY' WITH WHAT IS INSIDE OF PARENTESIS, SO IF WE DON'T USE '?:'(non-overlapping)
findall WILL GIVES US ONLY THE MATCHES THAT ARE INSIDE OF THE PARENTHESIS. SO THAT'S THE REASON WHY WE COULDN'T GET THE SAME
RESULT AS WE DID WITH 'match'.
also to remember: 'findall' gives all the ocurrences that finds in the entire string, even if they are in separate
parts of the string, while 'match' will gives ud the entire ocurrences, from the start to the end. (aparently
it doesn't match what is inside of the parentesis first)""" 
result = re.findall(pattern_to_practice, 'kenifer@gmail.edu.co')
print(result)




# Product inventory #


"""2. **Exercise 2: Product Inventory**
   - Create a `Product` model with fields: `product_id`, `product_name`, `product_category`, `price`, and `quantity_in_stock`.
   - The `product_id` should be a unique identifier.
   - The `product_name` should be a string and cannot be empty.
   - The `product_category` should be one of the following: 'Electronics', 'Clothing', 'Grocery'.
   - The `price` should be a positive float.
   - The `quantity_in_stock` should be a positive integer.
   - Use a JSON file named `product_inventory.json` to test your model.
"""

from pydantic import field_validator, Field
from typing import Literal
from typing_extensions import Literal
from pydantic import PositiveFloat, PositiveInt

inventory_path = 'C:/Users/kenifer/Desktop/pruebas-json/products.json'

try:
    with open(inventory_path, encoding='utf8') as inventory_file:
        inventory_information = json.load(inventory_file)

except FileNotFoundError:
    print(f'The file {inventory_path} does not exist.')


class InventoryErrors(Exception):
    def __init__(self, value=None, message=None):
        self.value = value
        self.message = message


class ProductInventory(BaseModel):
    product_id: int 
    product_name: str 
    product_category: Literal['Electronics', 'Grocery', 'Clothing']
    price: PositiveFloat
    quantity_in_stock: PositiveInt

    @field_validator('product_id') # Couldn't solve this validation because of the ORM lack of knowledges.
    @classmethod
    def product_id_validator(cls, value):
        return value
        

    @field_validator('product_name')
    @classmethod
    def product_name_validator(cls, value):
        """Doing the logic for the product_name validator"""
        if len(value) <= 1:
            raise PydanticCustomError(
                'string_length_error',
                'String must have at least 1 character!',
                {'input_string': value})

        return value
    
    

try:
    class_information: List[ProductInventory] = [ProductInventory(**item) for item in inventory_information['products']]
    print(class_information)

except ValidationError as msj:
    print(msj)




# BOOK COLLECTION #
    
"""3. **Exercise 3: Book Collection**
   - Create a `Book` model with fields: `isbn`, `title`, `author`, `publication_date`, and `pages`.
   - The `isbn` should be a valid ISBN-10 or ISBN-13 number.
   - The `title` and `author` should be strings and cannot be empty.
   - The `publication_date` should be a date and cannot be in the future.
   - The `pages` should be a positive integer.
   - Use a JSON file named `book_collection.json` to test your model."""

from pydantic import BaseModel, Field, field_validator
from fastapi import HTTPException, status, FastAPI


book_collection_path = 'C:/Users/kenifer/Desktop/pruebas-json/books.json'

app = FastAPI()

@app.get('/openfile')
async def open_file():
    try:
        book_file = open(book_collection_path)
        json_file = json.load(book_file)

    except FileNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='The file was not found.')
    
    return json_file


class BookCollection(BaseModel):
    isbn: int
    title: str
    author: str
    publication_date: datetime
    pages: int


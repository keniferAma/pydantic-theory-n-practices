from pydantic import BaseModel, validator, ValidationError
import datetime 
from typing import Tuple # Tuple es basicamente tuple, de la estructura original de python, solo que en estos casos
# nos va a servir para que nuestro código quede mas legible y comprensible, al tiempo de que mejora la eficiencia y por
# último porque así está siendo adoptado por fastapi, pydantic y la comunidad de desarrolladores.

class Student(BaseModel):
    student_name: str
    student_surname: str
    age: int
    date_enrolled: datetime.date

    @validator("age") # un string con el nombre del la key que queremos validar, en este caso "age"
    def age_validation(cls, value): # dicho valor del decorador automáticamente pasa al parametro "value"
        if value < 18:
            return "Debes ser mayor de edad"
        else:
            return value


student1 = Student(
    student_name="kenifer",
    student_surname="amariles",
    age=5,
    date_enrolled=datetime.date(2021,4,4)
)

print(student1)
"""student_name='kenifer' student_surname='amariles' age=5 date_enrolled=datetime.date(2021, 4, 4)"""
# Esta es una de las particularidades de Basemodel, y es que me imprime la información sin la necesidad de tener
# un método asignado para ello. En una clase normalemente me dara la dirección de la información en memoria.


from datetime import datetime
from pydantic import PositiveInt

class User(BaseModel):
    id: int  
    name: str = 'John Doe' # podemos dar valor con cualquier string, sin embargo tenemos un nombre predeterminado 
    signup_ts: datetime | None  # puede ser bien sea un datetime o un valor nulo.
    tastes: dict[str, PositiveInt]  # estamos definiendo un diccionario con un str como key y un
    # número positivo como valor.



# un pequeño recordatorio del desempaquetado con listas:

def desempaquetado(nombre, edad, nacionalidad):
    return f"{nombre} con {edad} años de edad, es de {nacionalidad}"

persona_ensayo = ["carlos", 30, "colombia"]

print(desempaquetado(*persona_ensayo))# un solo asterisco debido a que se trata de una lista.



### ALGUNOS CONCEPTOS PARA TENER EN CUENTA Y COMPRENDER AÚN MAS LAS DIFERENCIAS ENTRE LOS DIFERENTES TIPOS DE MÉTODOS
# EL MÉTODO DE CLASE, DEFINITIVAMENTE NO VA A ACCEDER A LO QUE SE ENCUENTRE TIPADO CON SELF 
class ClasePrueba:
    numero_de_personas = 1

    def __init__(self, nombre, edad) -> None:
        self.nombre = nombre
        self.edad = edad
        ClasePrueba.numero_de_personas += 1
        # Nótese aquí que ClasePrueba solo puede acceder a lo que NO esté con "self", al parecer lo que no
        # se encuentra en la clase contructor.

    def andar(self, caminar):
        self.caminar = caminar
        self.numero_de_personas


    @classmethod
    def contador_personas(cls):
        return cls.numero_de_personas
    
ClasePrueba.contador_personas # SIN VARIABLE DE INSTANCIA NO PUEDO ACCEDER A LOS ATRIBUTOS DEL CONSTRUCTOR NI A LOS "self"
ClasePrueba.andar # PODEMOS ACCEDER A LOS METODOS, A CUALQUIERA

ClasePrueba("alejandro", 23).edad # PASANDO LOS ARGUMENTOS SI PODEMOS ACCEDER A LOS ATRIBUTOS.

persona_1 = ClasePrueba("alejandro", 23)
persona_2 = ClasePrueba("hernando", 45)

print(persona_1.numero_de_personas) # YA TENIENDO EL OBJETO PODEMOS ACCEDER DESDE ESTE A CUALQUIER VARIABLE 
# INCLUSIVE SI ESTÁN FUERA DEL CONSTRUCTOR.
# Otra curiosidad es el conteo que usamos para el ejemplo, ya que este método nos cuenta cada una de las instancias
# y las suma a "numero de personas"

print(persona_1)
    
# VAMOS A CREAR UN EJEMPLO CON TODOS LOS DATOS CORRECTOS CON EL FIN DE OBSERVAR EL FUNCIONAMIENTO DE UNA PLANTILLA:

from datetime import datetime

from pydantic import BaseModel, PositiveInt
# Es muy importante usar este tipo de tipado, "PositiveInt" en este caso, ya que haciendolo así obtenemos 
# varios beneficios, por ejemplo, informacion acerca de errores; debido a que pydantic tiene implementado estos
# valores en su sistema, y por ende nos va a generar la información detallada de cada error.
# Otra de las ventajas está relacionada con la legibilidad del código, y otra es la facilidad de usarlo en 
# cualquier situación.


class User(BaseModel):
    id: int  
    name: str = 'kenifer alejandro'  
    signup_ts: datetime | None  
    tastes: dict[str, PositiveInt]  


external_data = {
    'id': 123,
    'signup_ts': '2019-06-01 12:22', # el datetime lo posemos pasar como un string con la estructura adecuada.  
    'tastes': {
        'wine': 9,
        b'cheese': 7,  
        'cabbage': '1', # PositiveInt también nos reconocerá strings con números.
    },
}

user = User(**external_data) # recordemos que cuando usamos el doble asterisco, estamos desempaquetando el diccionario
# con los valores que requiere la plantilla.
print(user.id)  
#> 123
print(user.model_dump()) # fastAPI hace literalmente todo esto.
# ESTE SERÍA EL RESULTADO SIN USAR "model_dump()" 
"""id=123 name='kenifer alejandro' signup_ts=datetime.datetime(2019, 6, 1, 12, 22) 
tastes={'wine': 9, 'cheese': 7, 'cabbage': 1}"""

# EL PROPOSITO PRINCIPAL DE USAR "model_dump()" es convertir el resultado que por defecto me arroja una representación de
# plantilla Basemodel, en un formato Json, como lo podemos observar en la siguiente salida.

"""
{
    'id': 123,
    'name': 'John Doe',
    'signup_ts': datetime.datetime(2019, 6, 1, 12, 22),
    'tastes': {'wine': 9, 'cheese': 7, 'cabbage': 1},
}
"""





# AHORA VAMOS A UTILIZAR EL MISMO CÓDIGO PERO USANDO TRY EXCEPT PARA CAPTURAR ALGUNOS ERRORES:


from pydantic import ValidationError # importamos para capturar errores
class User(BaseModel):
    id: int  
    name: str = 'kenifer alejandro'  
    signup_ts: datetime | None  
    tastes: dict[str, PositiveInt] # Notemos también que usamos siempre corchetes al momento de especificar, en este
    # caso la clave y el valor del diccionario, las notaciones, y esto debido a que pydantic junto con varias librerias
    # adoptan este tipo de estructuras. además de que estaríamos especificando que vamos a esperar un resultado iterable
    # o una lista.


external_data = {
    'id': 123,
    'signup_ts': '2019-06-01 12:22',  
    'tastes': {
        'wine': 9,
        b'cheese': -3, # Inducimos a error usando el value, un int negativo para sacar una excepción.
        'cabbage': '1',  
    },
}

try:
    user = User(**external_data)

except ValidationError as e:
    print(e.json()) # La documentación nos señala usar "e.error", sin embargo nos arroja el resultado en memoria
    # entonces usamos un método json y esta vez nos muestra por consola el error que estamos atravesando.
    
"""[{
    "type":"greater_than",
    "loc":["tastes","b'cheese'"],
    "msg":"Input should be greater than 0",
    "input":-3,"ctx":{"gt":0},
    "url":"https://errors.pydantic.dev/2.0.3/v/greater_than"
    
}]"""


                                        ### ANNOTATED - LITERAL ###


from typing import Annotated, Dict, List, Literal, Tuple

from annotated_types import Gt

from pydantic import BaseModel


class Fruit(BaseModel):
    name: str  
    color: Literal['red', 'green'] # Basicamente debe ser el valor literal, en este caso red o green
    weight: Annotated[float, Gt(0)]  #Annotated[type, annotation1, annotation2, ...]
    # Las anotaciones pueden ser cualquier objeto o valor que desees utilizar para describir o agregar 
    # información adicional al tipo de dato. Estas anotaciones no tienen ningún efecto en la validación o 
    # comportamiento del código, son simplemente utilizadas para propósitos informativos o de documentación.
    # Del segundo valor en adelante no tiene por qué intervenir en el proceso de pydantic, ya que, como su nombre
    # lo indica, son simples anotaciones o información adicional.
    # Como ejemplo podriamos usar 'name: Annotated[str, "name of the student"]' especificando que es lo que va a recibir
    # a modo de comentario dentro de la misma notación.
    bazam: Dict[str, List[Tuple[int, bool, float]]]# int, bool, float deben si o si estar. 


print(
    Fruit(
        name='Apple',
        color='red',
        weight=4.2,
        bazam={'foobar': [(1, True, 0.1)]},
    )
)
#> name='Apple' color='red' weight=4.2 bazam={'foobar': [(1, True, 0.1)]}





                                ## EJEMPLO DE ESQUEMA JSON ##
### Al parecer "model_json_schema()" nos proporciona información en formato json para documentación.

from datetime import datetime

from pydantic import BaseModel


class Address(BaseModel):
    street: str
    city: str
    zipcode: str


class Meeting(BaseModel):
    when: datetime
    where: Address
    why: str = 'No idea'


print(Meeting.model_json_schema())
"""
{
    '$defs': {
        'Address': {
            'properties': {
                'street': {'title': 'Street', 'type': 'string'},
                'city': {'title': 'City', 'type': 'string'},
                'zipcode': {'title': 'Zipcode', 'type': 'string'},
            },
            'required': ['street', 'city', 'zipcode'],
            'title': 'Address',
            'type': 'object',
        }
    },
    'properties': {
        'when': {'format': 'date-time', 'title': 'When', 'type': 'string'},
        'where': {'$ref': '#/$defs/Address'},
        'why': {'default': 'No idea', 'title': 'Why', 'type': 'string'},
    },
    'required': ['when', 'where'],
    'title': 'Meeting',
    'type': 'object',
}
"""






                                ##### model_validate #####
# Normalemente si queremos ejecutar un objeto o instancia bien sea por un print o un return lo que hacemos es 
# especificar cada uno de los valores de la clase (es decir, asignar valores) en los argumentos de dicha clase.
# Y en este caso en específico estamos dando como argumentos un formato Json, que, en términos normales sería 
# imposible y nos va a sacar error. (mediante desempaquetado SI es posible).
# Pero en este caso usamos el método model_validate, el cual nos permite dar como
# argumento una cadena Json, pero, como lo podemos observar en el ejemplo debe tener sus respectivas claves con
# el valor exacto.


print("/////////")

class User(BaseModel):
    id: int  
    name: str = 'kenifer alejandro'  
    signup_ts: datetime | None  
    tastes: dict[str, PositiveInt]

user_print = User.model_validate({"id": 123, "name": "Leandro", 
                   "signup_ts": "2020-01-01T12:00", 
                   "tastes": {"hola": 2}})

print(user_print)
"""id=123 name='Leandro' signup_ts=datetime.datetime(2020, 1, 1, 12, 0) tastes={'hola': 2}"""
######    OJO ESTO SERÍA UNA REPRESENTACIÓN DE TIPO __repr__!!!!!!
# siempre estuvo la confusión debido a la extraña estructura que para mí no entraba en ningún tipo.


class User(BaseModel):
    id: int  
    name: str = 'kenifer alejandro'  
    signup_ts: datetime | None  
    tastes: dict[str, PositiveInt]


try:
    user_print = User.model_validate({"id": 123, "name": "Leandro", 
                    "signup_ts": "2020-01-01T12:00", 
                    "tastes": {"hola": 2}}, strict=True)# strict mode, este modo es para manejar de manera 
    # estricta las claves y valores que vamos a ingresar (de por si las claves deben ser estrictamente los mismos valores)
    # ;en este caso no tenemos de manera "estricta" el formato de tiempo en el campo valor de "signup_ts". por 
    # consiguiente pasamos todo a un try except para capturar el evidente error que vamos a generar.
    # Y ES DE MANERA ESTRICTA, CON LAS NORMAS ESTABLECIDAS PARA DICHOS PARÁMETROS.

    ## NOTA: CON model_validate PODEMOS GUARDAR LA INFORMACIÓN EN UNA VARIABLE PARA LUEGO DESEMPAQUETARLA CON DOBLE 
    ## ASTERISCO, ESTO DEBIDO A QUE CON LO QUE ESTAMOS TRABAJANDO ES CON UN DICCIONARIO O CON UN JSON DIRECTAMENTE.
    ## LO CUAL ES ALGO INNECESARIO DEBIDO A QUE EL DESEMPAQUETADO ES POR DEFECTO TENGA O NO model_validate.
    
    
except ValidationError as validation_error:
    print(validation_error)
    """1 validation error for User
    signup_ts
    Input should be a valid datetime [type=datetime_type, input_value='2020-01-01T12:00', input_type=str]
    For further information visit https://errors.pydantic.dev/2.0.3/v/datetime_type
    """









                                    ### model_validate_json ####
## la diferencia principal es casi obvia, es decir, mientras que model_validate nos valida y nos recibe informacion en 
# formato Json o diccionario, model_validate_json nos recibe información de strings con estructura Json.

class Meeting(BaseModel):
    when: datetime
    where: bytes

m_json = Meeting.model_validate_json(
    '{"when": "2020-01-01T12:00", "where": "home"}'
)
print(m_json)






                    #### model_json_schema() ####
## basicamente nos proporciona información detallada de la plantilla u objeto, y todo en formato json, además de que
# nos funciona como documentación.


from pydantic import BaseModel


class Address(BaseModel):
    street: str
    city: str
    zipcode: str


class Meeting(BaseModel):
    when: datetime
    where: Address
    why: str = 'No idea'


print(Meeting.model_json_schema())
"""
{
    '$defs': {
        'Address': {
            'properties': {
                'street': {'title': 'Street', 'type': 'string'},
                'city': {'title': 'City', 'type': 'string'},
                'zipcode': {'title': 'Zipcode', 'type': 'string'},
            },
            'required': ['street', 'city', 'zipcode'],
            'title': 'Address',
            'type': 'object',
        }
    },
    'properties': {
        'when': {'format': 'date-time', 'title': 'When', 'type': 'string'},
        'where': {'$ref': '#/$defs/Address'},
        'why': {'default': 'No idea', 'title': 'Why', 'type': 'string'},
    },
    'required': ['when', 'where'],
    'title': 'Meeting',
    'type': 'object',
}
"""

"""En este caso, el esquema JSON generado muestra la estructura y las validaciones de los modelos Address y Meeting:

Para el modelo Address:

El esquema muestra que Address es un objeto que contiene tres propiedades: street, city y zipcode.
Cada propiedad tiene un tipo string, lo que significa que se espera que los valores de estas propiedades sean 
cadenas de texto.
Todas las propiedades son requeridas (required) ya que no tienen un valor predeterminado.
Para el modelo Meeting:

El esquema muestra que Meeting es un objeto que contiene tres propiedades: when, where y why.
La propiedad when tiene el tipo string con el formato date-time, lo que indica que se espera que los valores 
de esta propiedad sean fechas y horas en formato ISO 8601.
La propiedad where hace referencia al esquema JSON del modelo Address, lo que significa que where debe ser un 
objeto que cumpla con las validaciones definidas en el modelo Address.
La propiedad why tiene el tipo string y tiene un valor predeterminado de 'No idea'.
El esquema JSON generado es útil para comprender la estructura y las validaciones definidas en los modelos 
Pydantic, lo que puede ser especialmente útil en el contexto de API web para definir las especificaciones y 
la documentación de los datos que se esperan en las solicitudes y respuestas.

En resumen, el método model_json_schema() de Pydantic te permite obtener un esquema JSON que describe 
la estructura y las validaciones de un modelo Pydantic, lo que puede ser útil para fines de documentación y 
comprensión de los datos esperados en tu aplicación.
"""






                            ### comprobación de salida con model_validate y salida normal ###
                            
# por default pydantic por medio de Basemodel nos puede forzar algunos datos con el fin de corregirlos, por ejemplo:
# en un atributo de tipo "int" podemos asignar un string con un número y automáticamente pydantic nos lo toma con un int, 
# y nos lo corrige en la salida.
# Sin embargo, cuando usamos model_validate() no es posible 
# EN ESTE EJEMPLO SI FUÉ NECESARIO USAR model_validate PARA QUE EL OBJETO ME PERMITIERA RECIBIR LOS ARGUMENTOS EN JSON.
# Y ESTO DEBIDO A QUE PARA PODER USAR UN JSON COMO ARGUMENTO PARA LA CLASE SIN USAR model_validate ES ESTRICTAMENTE 
# NECESARIO GUARDAR LA INFORMACIÓN CON EL JSON EN UNA VARIABLE, Y YA LUEGO DESDE AQUÍ PASARLA AL ARGUMENTO DE LA CLASE
# EN MODO DE DESEMPAQUETADO.
# ENTONCES, RESUMIENDO: model_validate SOLAMENTE CUANDO DAMOS LOS ARGUMENTOS DIRECTAMENTE A LA CLASE, SIN INSTANCIA
# Y PARA PASAR UN JSON DE LA MANERA TRADICIONAL, DEBE SER GUARDANDOLO EN UNA VARIABLE Y POSTERIORIMENTE DESEMPAQUETANDOLA.

# ALGO TAMBIÉN A DESTACAR CON model_validate ES EL HECHO QUE ES MÁS ESTRICTO EN CUANTO A SUS PROPIEDADES, ES DECIR,
# POR EJEMPLO CON UN JSON TRADICIONAL PYDANTIC ES MUY VERSÁTIL Y UN STRING CON UN INT DENTRO, ME LO TOMA COMO UN INT
# MIENTRAS QUE CON model_validate SE TORNA IMPOSIBLE HACERLO DE ESA MANERA.

class User(BaseModel):
    id: int  
    name: str = 'kenifer alejandro'  
    signup_ts: datetime | None  
    tastes: dict[str, PositiveInt]



user_print = User.model_validate({'id': 23, 'name':'alejandro', 'signup_ts': datetime.now(), 'tastes':{
    'persona': 3
}})# Este json solamente es posible mediante model_validate, debido a que lo estamos pasando directamente, sin
# desempaquetar.

print(user_print)
"""id=123 name='Leandro' signup_ts=datetime.datetime(2020, 1, 1, 12, 0) tastes={'hola': 2}""" #con model_validate
"""id=23 name='alejandro' signup_ts=datetime.datetime(2023, 8, 2, 12, 42, 40, 557787) tastes={'persona': 3}""" #sin model_validate

    




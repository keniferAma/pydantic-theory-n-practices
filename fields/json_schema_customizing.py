"""There are fields that exclusively to customise the generated JSON Schema:

-title: The title of the field.
-description: The description of the field.
-examples: The examples of the field.
-json_schema_extra: Extra JSON Schema properties to be added to the field."""


from pydantic import BaseModel, EmailStr, Field, SecretStr


class User(BaseModel):
    age: int = Field(description='Age of the user')
    email: EmailStr = Field(examples=['marcelo@mail.com'])
    name: str = Field(title='Username')
    password: SecretStr = Field(
        json_schema_extra={
            'title': 'Password',
            'description': 'Password of the user',
            'examples': ['123456'],
        }
    )


print(User.model_json_schema())
"""
{
    'properties': {
        'age': {
            'description': 'Age of the user',
            'title': 'Age',
            'type': 'integer',
        },
        'email': {
            'examples': ['marcelo@mail.com'],
            'format': 'email',
            'title': 'Email',
            'type': 'string',
        },
        'name': {'title': 'Username', 'type': 'string'},
        'password': {
            'description': 'Password of the user',
            'examples': ['123456'],
            'format': 'password',
            'title': 'Password',
            'type': 'string',
            'writeOnly': True,
        },
    },
    'required': ['age', 'email', 'name', 'password'],
    'title': 'User',
    'type': 'object',
}
"""

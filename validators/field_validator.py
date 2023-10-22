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
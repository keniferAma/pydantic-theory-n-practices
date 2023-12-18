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


"""When you instantiate PydanticCustomError, you need to provide three arguments1:

error_type: A string that represents the type of error.
message_template: A string that serves as a template for the error message.
context: An optional dictionary that can contain additional context for the error."""
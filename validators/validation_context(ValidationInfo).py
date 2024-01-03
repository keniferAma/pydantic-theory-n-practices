from pydantic import BaseModel, ValidationInfo, field_validator


class Model(BaseModel):
    text: str

    @field_validator('text')
    @classmethod
    def remove_stopwords(cls, v: str, info: ValidationInfo):
        context = info.context # I did not know we can give context as the extra argument.
        if context:
            stopwords = context.get('stopwords', set())
            v = ' '.join(w for w in v.split() if w.lower() not in stopwords)
        return v


data = {'text': 'This is an example document'}
print(Model.model_validate(data))  # no context
#> text='This is an example document'
print(Model.model_validate(data, context={'stopwords': ['this', 'is', 'an']}))
#> text='example document'
print(Model.model_validate(data, context={'stopwords': ['document']}))
#> text='This is an example'






from typing import Any, Dict, List

from pydantic import (
    BaseModel,
    ValidationError,
    ValidationInfo,
    field_validator,
)

_allowed_choices = ['a', 'b', 'c']


def set_allowed_choices(allowed_choices: List[str]) -> None:
    global _allowed_choices
    _allowed_choices = allowed_choices


def get_context() -> Dict[str, Any]:
    return {'allowed_choices': _allowed_choices}



class Model(BaseModel):
    choice: str

    @field_validator('choice')
    @classmethod
    def validate_choice(cls, v: str, info: ValidationInfo):
        allowed_choices = info.context.get('allowed_choices')
        if allowed_choices and v not in allowed_choices:
            raise ValueError(f'choice must be one of {allowed_choices}')
        return v


print(Model.model_validate({'choice': 'a'}, context=get_context()))
#> choice='a'

try:
    print(Model.model_validate({'choice': 'd'}, context=get_context()))
except ValidationError as exc:
    print(exc)
    """
    1 validation error for Model
    choice
      Value error, choice must be one of ['a', 'b', 'c'] [type=value_error, input_value='d', input_type=str]
    """

set_allowed_choices(['b', 'c'])

try:
    print(Model.model_validate({'choice': 'a'}, context=get_context()))
except ValidationError as exc:
    print(exc)
    """
    1 validation error for Model
    choice
      Value error, choice must be one of ['b', 'c'] [type=value_error, input_value='a', input_type=str]
    """



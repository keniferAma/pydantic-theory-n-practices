from datetime import datetime, timedelta, timezone
from typing import Any, Dict

from pydantic import BaseModel, ConfigDict, field_serializer, model_serializer


class WithCustomEncoders(BaseModel):
    model_config = ConfigDict(ser_json_timedelta='iso8601')

    dt: datetime
    diff: timedelta

    @field_serializer('dt')
    def serialize_dt(self, dt: datetime, _info):
        return dt.timestamp()


m = WithCustomEncoders(
    dt=datetime(2032, 6, 1, tzinfo=timezone.utc), diff=timedelta(hours=100)
)
print(m.model_dump_json())
#> {"dt":1969660800.0,"diff":"P4DT14400S"}
print(m) # without calling any dict/json model.
"""dt=datetime.datetime(2032, 6, 1, 0, 0, tzinfo=datetime.timezone.utc) diff=datetime.timedelta(days=4, seconds=14400)"""

class Model(BaseModel):
    x: str

    @model_serializer
    def ser_model(self) -> Dict[str, Any]:
        return {'x': f'serialized {self.x}'}


print(Model(x='test value').model_dump_json())
#> {"x":"serialized test value"} # The dict/json models print the information we set at the decorator.

user_without_serializer_decorator = Model(x='Without')
print(user_without_serializer_decorator)
"""x='Without'""" # Here we can see, that the no dict or json data will avoid the decorator.



"""
*max_digits: Maximum number of digits within the Decimal. It does not include a zero before the decimal 
point or trailing decimal zeroes.
*decimal_places: Maximum number of decimal places allowed. It does not include trailing decimal zeroes.
"""

from decimal import Decimal

from pydantic import BaseModel, Field


class Foo(BaseModel):
    precise: Decimal = Field(max_digits=5, decimal_places=2)


foo = Foo(precise=Decimal('123.45'))
print(foo)
#> precise=Decimal('123.45')

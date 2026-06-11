from typing import Optional
from pydantic import BaseModel, ConfigDict
from vocal.field import Field

class VariableAttributes(BaseModel):
    model_config = ConfigDict(
        # Configuration options here
        title='Variable Attributes',
        extra='allow'
    )

    # Add your attributes here, e.g.
    #
    # my_attribute: str = Field(
    #   description='A description of my attribute',
    #   example='my_attribute_value'
    # )
    standard_name: Optional[str] = Field(
        description='Standard name for this variable',
        example='standard_name_value',
        default=None
    )

    # blah: str = Field(
    #     description='blah',
    #     example='blah_value'
    # )

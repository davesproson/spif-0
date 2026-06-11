
from pydantic import BaseModel
from typing import List

from vocal.netcdf.mixins import VariableNetCDFMixin
from vocal.field import Field

from ..attributes import VariableAttributes


class VariableMeta(BaseModel):
    datatype: str = Field(description='The type of the data')
    name: str
    required: bool = True


class Variable(BaseModel, VariableNetCDFMixin):
    meta: VariableMeta
    dimensions: List[str]
    attributes: VariableAttributes

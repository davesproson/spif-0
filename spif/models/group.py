
from __future__ import annotations
from typing import Optional

from cfunits import Units
from pydantic import BaseModel, ConfigDict
from vocal.netcdf.mixins import GroupNetCDFMixin
from vocal.validation import (
    validator,
    variable_exists,
    dimension_exists,
    group_exists,
    variable_has_types,
    variable_has_dimensions,
    substitutor,
)

from ..attributes.group_attributes import (
    GenericGroupAttributes, PlatformGroupAttributes
)

from ..attributes import  ImagerGroupAttributes, CoreGroupAttributes

from .dimension import Dimension
from .variable import Variable

# Define some data types for use in the group schema validators
FLOATS = [f'<float{i}>' for i in [16, 32, 64, 128]]
INTS = [f'<int{i}>' for i in [8, 16, 32, 64]]
UINT8 = ['<uint8>', '<ubyte>']
INT8 = ['<int8>', '<byte>']
UINTS = UINT8 + [f'<uint{i}>' for i in [16, 32, 64]]
UINT64 = ['<uint64>']


def core_group(func):
    """
    A decorator which will only apply a validator to the 'core' group
    """
    def wrapper(cls, values):
        name = values.meta.name
        if name != 'core':
            return values
        return func(cls, values)
    return wrapper
    


class GroupMeta(BaseModel):
    model_config = ConfigDict(
        title='Group Metadata'
    )

    name: str

class GenericGroup(BaseModel, GroupNetCDFMixin):
    model_config = ConfigDict(
        title='Group Schema'
    )

    meta: GroupMeta
    attributes: GenericGroupAttributes
    dimensions: Optional[list[Dimension]] = None
    variables: list[Variable]
    groups: Optional[list[GenericGroup]] = None


class PlatformGroup(BaseModel, GroupNetCDFMixin):
    model_config = ConfigDict(
        title='Group Schema'
    )

    meta: GroupMeta
    attributes: PlatformGroupAttributes
    dimensions: Optional[list[Dimension]] = None
    variables: list[Variable]
    groups: Optional[list[GenericGroup]] = None


class CoreGroup(BaseModel, GroupNetCDFMixin):
    model_config = ConfigDict(
        title='Group Schema'
    )

    meta: GroupMeta
    attributes: CoreGroupAttributes
    dimensions: list[Dimension]
    variables: list[Variable]
    groups: Optional[list[GenericGroup]] = None

    # Ensure that the 'core' group has the required variables
    _validate_for_image_variable = variable_exists('image')
    _validate_for_timestamp_variable = variable_exists('timestamp')
    _validate_for_startpixel_variable = variable_exists('startpixel')
    _validate_for_width_variable = variable_exists('width')
    _validate_for_height_variable = variable_exists('height')
    _validate_for_overload_variable = variable_exists('overload')

    # Ensure that the 'core' group has the required dimensions
    _validate_for_image_num_dimension = dimension_exists('image_num')
    _validate_for_pixel_dimension = dimension_exists('pixel')

    # Ensure that variables have the correct dimensions
    _validate_image_dims = variable_has_dimensions('image', ['pixel'])
    _validate_timestamp_dims = variable_has_dimensions('timestamp', ['image_num'])
    _validate_startpixel_dims = variable_has_dimensions('startpixel', ['image_num'])
    _validate_width_dims = variable_has_dimensions('width', ['image_num'])
    _validate_height_dims = variable_has_dimensions('height', ['image_num'])
    
    # Check that variables have the correct type
    _validate_image_has_correct_type = variable_has_types('image', UINT8)
    _validate_timestamp_has_correct_type = variable_has_types('timestamp', UINT64)
    _validate_startpixel_has_correct_type = variable_has_types('startpixel', UINTS)
    _validate_width_has_correct_type = variable_has_types('width', UINTS)
    _validate_height_has_correct_type = variable_has_types('height', UINTS)
    _validate_overload_has_correct_type = variable_has_types('overload', INT8)

    # Ensure that required dimensions are unlimited size
    #@validator
    @core_group
    def check_unlimited_dimensions(cls, values):
        dimensions = values.dimensions
        if dimensions is None:
            return values # No dimensions to check - this will be caught in the dimension_exists validator
        name = values.meta.name
        for dim in dimensions:
            if dim.name in ['image_num', 'pixel']:
                if dim.size != None:
                    raise ValueError(f'{name} - The \'{dim.name}\' dimension must be unlimited size')
        return values

    #@validator 
    @core_group
    def check_time_units_valid(cls, values):
        try:
            variables = values.variables
        except Exception:
            variables = []
        valid_unit = Units('seconds since 1970-01-01 00:00:00')
        if variables is None:
            return values
        for var in variables:
            if var.meta.name == 'timestamp':
                units = getattr(var.attributes, 'units', None)
                if units is None:
                    raise ValueError(f'\'timestamp\' variable must have a units attribute')
                if not Units(units).isvalid:
                    raise ValueError(f'\'timestamp\' variable units not valid (got {units})')
                if not Units(units).equivalent(valid_unit):
                    raise ValueError(f'\'timestamp\' variable units must be equivalent to \'{valid_unit}\'')
        return values

    #@validator
    @core_group
    def check_timestamp_variable_standard_name(cls, values):
        try:
            variables = values.variables
        except Exception:
            variables = []
        if variables is None:
            return values
        for var in variables:
            if var.meta.name == 'timestamp':
                standard_name = getattr(var.attributes, 'standard_name', None)
                if standard_name is None:
                    raise ValueError(f'\'timestamp\' variable must have a standard_name attribute')
                if standard_name != 'time':
                    raise ValueError(f'\'timestamp\' variable standard_name must be \'time\'')
        return values
    
    @substitutor
    def substitute_time_units(cls, values):
        """
        Replace the timestamp units with a valid units string if it is specified
        as being derived from file
        """
        variables = values.get('variables', [])

        for var in variables:
            if var['meta']['name'] == 'timestamp':
                units = var.get('attributes', {}).get('units', None)
                if units is not None and 'derived_from_file' in units:
                    var['attributes']['units'] = 'seconds since 1970-01-01T00:00:00Z'
        return values


class ImagerGroup(BaseModel, GroupNetCDFMixin):
    model_config = ConfigDict(
        title='Imager Group Schema'
    )

    meta: GroupMeta
    attributes: ImagerGroupAttributes
    dimensions: list[Dimension]
    groups: list[CoreGroup | GenericGroup]
    variables: list[Variable]

    # Ensure that the 'core' group exists
    _validate_core_group_exists = group_exists('core')

    # Ensure that the 'imager' group has the correct variables
    _validate_color_level_variable_exists = variable_exists('color_level')
    _validate_array_size_variable_exists = variable_exists('array_size')
    _validate_image_size_variable_exists = variable_exists('image_size')
    _validate_resolution_variable_exists = variable_exists('resolution')
    _validate_wavelength_variable_exists = variable_exists('wavelength')
    _validate_pathlength_variable_exists = variable_exists('pathlength')

    # Ensure that the 'imager' group has the correct dimensions
    _validate_array_dimensions_dimension_exists = dimension_exists('array_dimensions')
    _validate_pixel_colors_dimension_exists = dimension_exists('pixel_colors')

    # Ensure required variables have the correct dimensions
    _validate_color_level_dims = variable_has_dimensions('color_level', ['pixel_colors'])
    _validate_array_size_dims = variable_has_dimensions('array_size', ['array_dimensions'])
    _validate_image_size_dims = variable_has_dimensions('image_size', ['array_dimensions'])
    _validate_resolution_dims = variable_has_dimensions('resolution', ['array_dimensions'])
    
    # Check that variables have the correct type
    _validate_color_level_has_correct_type = variable_has_types('color_level', FLOATS)
    _validate_array_size_has_correct_type = variable_has_types('array_size', INTS)
    _validate_image_size_has_correct_type = variable_has_types('image_size', INTS)
    _validate_resolution_has_correct_type = variable_has_types('resolution', FLOATS)
    _validate_wavelength_has_correct_type = variable_has_types('wavelength', FLOATS)
    _validate_pathlength_has_correct_type = variable_has_types('pathlength', FLOATS)

    #@validator
    def array_dimensions_dimension_size_1_or_2(cls, values):
        """
        array_dimensions dimension must have a size of 1 or 2
        """
        dims = values.dimensions

        fail_msg = (f'The \'array_dimensions\' dimension must have a ' 
                    'size of 1 or 2')

        try:
            for dim in dims:
                if dim.name == 'array_dimensions':
                    if dim.size not in [1, 2]:
                        raise ValueError(fail_msg)
                    return values
        except Exception:
            # No dimensions defined, fall through to fail
            pass

        raise ValueError(fail_msg)

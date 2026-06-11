"""
Summary of SPIF Requirements by Group Type
==========================================

Root Group
----------

Mandatory Attributes:
^^^^^^^^^^^^^^^^^^^^^

    :Conventions: A space or comma delineated list of conventions given in a
        single string. Must include "SPIF-m.n" where m.n is the version number.
    :imager_groups: A space- or comma-delineated string of *imager* group
        names.


Mandatory Groups:
^^^^^^^^^^^^^^^^^

    * Must contain at least one *imager* group


/*Imager* Group
---------------

Mandatory Attributes:
^^^^^^^^^^^^^^^^^^^^^

    :group_type: Must be "imager"
    :instrument_name: Short name of the imaging instrument. It may be the same as
        the group name.


Mandatory Dimensions:
^^^^^^^^^^^^^^^^^^^^^

    :pixel_colors: Number of color levels in image
    :array_dimensions: Number of dimensions of imaging array


Mandatory Variables:
^^^^^^^^^^^^^^^^^^^^

    ``float32`` **color_level**\ (pixel_colors):
        Lower bound of fractional obscuration/grayscale/color level for each
        `color_value` used in image data.

    ``int32`` **array_size**\ (array_dimensions):
        Number of pixels on the detector in each `array_dimension`.

    ``int32`` **image_size**\ (array_dimensions):
        Number of pixels across an image. If fixed size then will be number
        of pixels, if variable size then use `_FillValue`.

    ``float32`` **resolution**\ (array_dimensions):
        Image resolution of instrument for each dimension.

    ``float32`` **wavelength**\ ():
        Operating wavelength of laser used for shadowing/imaging the particles.

    ``float32`` **pathlength**\ ():
        Optical path length of imaging region.


Mandatory Groups:
^^^^^^^^^^^^^^^^^

    * Must contain one (and only one) 'core' group.


/*Imager*/Core Group
--------------------

Mandatory Attributes:
^^^^^^^^^^^^^^^^^^^^^

    :group_type: Must be "core"


Mandatory Dimensions:
^^^^^^^^^^^^^^^^^^^^^

    :image_num *unlimited*\ : Number of images in data
    :pixel *unlimited*\ : Number of pixels in data


Mandatory Variables:
^^^^^^^^^^^^^^^^^^^^

    ``uint8`` **image**\ (pixel):
        Flattened array of image pixel color values.

    ``uint64`` **timestamp**\ (image_num):
        Arrival time, relative to a reference start time, of the first pixel
        of an image.

        :standard_name: Must be "time"
        :units: Must be UDUNITS compliant string

    ``uint32`` **startpixel**\ (image_num):
        Array index of first pixel of an image.

    ``uint8`` **width**\ (image_num):
        Number of pixels across an image.

    ``uint8`` **height**\ (image_num):
        Number of slices/lines in an image.

    ``byte`` **overload**\ (image_num):
        Flag indicating an imager overload condition for each image.


/Platform Group (optional)
--------------------------

A 'platform' group may be included in the root that contains data relevant to
the platform on which the imager was operated. If this was an aircraft then
variables in this group may be ``altitude``, ``latitude``, ``longitude``,
``tas``, etc. Users are encouraged to consider CF conventions for these
variable types.

There are currently no *vocal* model requirements on the 'platform' group
in addition to an 'other' type group. It has been included as a specific
`group_type` however to allow for this in the future.

Mandatory Attributes:
^^^^^^^^^^^^^^^^^^^^^

    :group_type: Must be "platform"


Any *Other* Group (optional)
----------------------------

The 'other' ``group_type`` is any other group that is not an '*imager*' or
'core' type group. These groups may be in the root or a sub-group of an
'*imager*' group.

Mandatory Attributes:
^^^^^^^^^^^^^^^^^^^^^

    :group_type: Must be "other"

"""


from . import models
from . import attributes
from . import defaults

# Use semantic-version package?
__version_definition__ = 0

__version__ = f'{__version_definition__}'

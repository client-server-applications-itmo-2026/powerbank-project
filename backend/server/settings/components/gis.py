import ctypes.util

from server.settings.components import config

GDAL_LIBRARY_PATH = config(
    "GDAL_LIBRARY_PATH",
    default=ctypes.util.find_library("gdal"),
)
GEOS_LIBRARY_PATH = config(
    "GEOS_LIBRARY_PATH",
    default=ctypes.util.find_library("geos_c"),
)

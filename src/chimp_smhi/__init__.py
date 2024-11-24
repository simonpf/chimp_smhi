"""The top-level package of the ``chimp_smhi``."""

from .extensions import SEVIRI, seviri_instance

__all__ = (
    "SEVIRI",
    "seviri_instance"
)

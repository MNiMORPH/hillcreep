"""hillcreep -- hillslope diffusivity built from a creep velocity profile.

``D`` is not a parameter here.  A student sets how fast soil creeps at the
surface per unit slope (``k_u``) and how quickly that motion decays with depth
(``dz_u``), and the diffusivity ``k_hs = k_u * dz_u`` is reported back as a
consequence.
"""

from ._version import __version__
from .hillslope import Hillslope
from .hillslope import River

__all__ = ["Hillslope", "River", "__version__"]

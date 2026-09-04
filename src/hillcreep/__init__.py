"""hillcreep -- hillslope diffusivity built from a creep velocity profile.

``D`` is not a parameter here.  A student sets how fast soil creeps at the
surface per unit slope (``K``) and how quickly that motion decays with depth
(``H_star``), and the diffusivity ``D = K * H_star`` is reported back as a
consequence.
"""

from ._version import __version__
from .hillslope import Hillslope
from .hillslope import River

__all__ = ["Hillslope", "River", "__version__"]

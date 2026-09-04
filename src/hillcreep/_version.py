#: Bump this on **every deploy**, even when nothing else changed.
#:
#: The compiled demos install this package by wheel filename, which is built
#: from the version. GitHub Pages serves wheels with ``cache-control:
#: max-age=600`` and there is no way to set a header, so a filename that does
#: not move means a returning reader silently reinstalls the *previous* wheel.
#:
#: That is not a theoretical tidiness point. On 2026-09-04 it shipped a
#: superseded transport rule to a reader who reported it as a bug, and then
#: broke a brand-new demo outright: the scarp app raised ``ImportError: cannot
#: import name 'Scarp'`` because the cached wheel predated the module.
__version__ = "0.1.0.dev2"

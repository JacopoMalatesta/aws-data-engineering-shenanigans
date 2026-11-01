"""Projen entry point.

Edit ``projen_setup.py`` (and ``projen_config.py``/``projen_types.py``),
then re-run ``npx projen`` to regenerate every projen-managed file. Never
hand-edit the managed files; they are read-only.
"""

# The logic lives in ``projen_setup.py`` because basedpyright cannot see
# this dot-prefixed file.

from projen_setup import set_up_project

set_up_project()

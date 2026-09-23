"""Locate the FCCWorkplace checkout so nothing here has to hardcode a user area.

Every path that lives *inside* the repository is derived from the repository
root, which is found by walking up from this file. Set FCCWORKPLACE_ROOT to
override (useful if the checkout has been renamed, or when a batch job stages
the scripts somewhere else).

Paths that point *outside* the repository stay absolute on purpose: the cvmfs
software area, the flavour-tagger models on /eos and the Delphes samples on
/gpfs are properties of the site, not of the checkout.

The FCCAnalyses stage scripts are loaded by `fccanalysis` through
importlib.spec_from_file_location, which does not put their directory on
sys.path, so they bootstrap this module with:

    import os, sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from repo_paths import analysis_path
"""

import os

# Files/directories that together identify the top of the checkout, used when
# the checkout has been renamed to something other than "FCCWorkplace".
_ROOT_MARKERS = ("setup.sh", "analysis", "FCCAnalyses")


def find_repo_root(start=None):
    """Return the absolute path of the FCCWorkplace checkout containing `start`.

    `start` defaults to this file. FCCWORKPLACE_ROOT wins if it is set.
    """
    override = os.environ.get("FCCWORKPLACE_ROOT")
    if override:
        root = os.path.abspath(os.path.expanduser(override))
        if not os.path.isdir(root):
            raise RuntimeError(
                f"FCCWORKPLACE_ROOT points at {root!r}, which is not a directory"
            )
        return root

    current = os.path.dirname(os.path.abspath(start or __file__))
    while True:
        named = os.path.basename(current) == "FCCWorkplace"
        marked = all(os.path.exists(os.path.join(current, m)) for m in _ROOT_MARKERS)
        if named or marked:
            return current
        parent = os.path.dirname(current)
        if parent == current:                      # hit "/" without a match
            raise RuntimeError(
                "could not locate the FCCWorkplace root above "
                f"{os.path.abspath(start or __file__)!r} — set FCCWORKPLACE_ROOT"
            )
        current = parent


REPO_ROOT = find_repo_root()
ANALYSIS_DIR = os.path.join(REPO_ROOT, "analysis", "Hbs", "mumu")


def repo_path(*parts):
    """Path relative to the FCCWorkplace root."""
    return os.path.join(REPO_ROOT, *parts)


def analysis_path(*parts):
    """Path relative to analysis/Hbs/mumu."""
    return os.path.join(ANALYSIS_DIR, *parts)

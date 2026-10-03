"""Basic import verification tests for Rocky package and subpackages."""

import importlib
import pytest
import rocky


def test_rocky_version():
    """Verify rocky package imports and has a valid version string."""
    assert hasattr(rocky, "__version__")
    assert isinstance(rocky.__version__, str)
    assert rocky.__version__ == "0.3.0"


@pytest.mark.parametrize(
    "subpackage",
    [
        "rocky.core",
        "rocky.audio",
        "rocky.language",
        "rocky.translation",
        "rocky.learning",
        "rocky.ui",
    ],
)
def test_subpackages_importable(subpackage: str):
    """Verify that every core architectural subpackage imports cleanly."""
    mod = importlib.import_module(subpackage)
    assert mod is not None
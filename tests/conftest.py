import sys
from unittest.mock import MagicMock

import pytest

# Mock IPython
sys.modules["IPython"] = MagicMock()
sys.modules["IPython.display"] = MagicMock()

from maplibreum.utils import IDGenerator

@pytest.fixture(autouse=True)
def reset_id_generator():
    """Reset the IDGenerator before every test to ensure deterministic output."""
    IDGenerator.reset()

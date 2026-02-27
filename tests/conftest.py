import sys
from unittest.mock import MagicMock

import pytest
from maplibreum.utils import IDGenerator

# Mock IPython
sys.modules["IPython"] = MagicMock()
sys.modules["IPython.display"] = MagicMock()

@pytest.fixture(autouse=True)
def reset_id_generator():
    """Reset the ID generator before each test to ensure deterministic example generation."""
    IDGenerator.reset()

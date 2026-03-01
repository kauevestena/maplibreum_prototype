import sys
from unittest.mock import MagicMock

# Mock IPython
sys.modules["IPython"] = MagicMock()
sys.modules["IPython.display"] = MagicMock()

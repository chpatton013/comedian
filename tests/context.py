import os
import sys

# Add the parent directory to the path so we can import the comedian module
# directly instead of relying on it to be installed in site-packages.
sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..')),
)

# Import and expose the comedian module for each test file.
import comedian
__all__ = ("comedian")

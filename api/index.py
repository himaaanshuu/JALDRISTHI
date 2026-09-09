import sys
import os

# Add api/ directory to path so local imports work
sys.path.insert(0, os.path.dirname(__file__))

from main import app

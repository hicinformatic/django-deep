from django.utils.version import get_version
from .manager import DeepManager
from .parser import DeepParser


VERSION = (0, 0, 1, 'beta', 0)

__version__ = get_version(VERSION)

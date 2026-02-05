import os
import shutil

from .gtfs import GTFS


__version__ = '0.1.5'


_TMP = os.path.join(os.path.realpath(os.path.dirname(__file__)), 'tmp')

if os.path.exists(_TMP): shutil.rmtree(_TMP)
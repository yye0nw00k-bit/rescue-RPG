"""Use a current Pygame source release for Android builds.

The stock python-for-android recipe may use an older Pygame release on
newer host Python toolchains. This override requests Pygame 2.6.1 instead.
The Android build still needs to be tested on a real device.
"""
from pythonforandroid.recipes.pygame import Pygame2Recipe


class Pygame261Recipe(Pygame2Recipe):
    version = "2.6.1"
    url = "https://github.com/pygame/pygame/archive/{version}.tar.gz"
    hostpython_prerequisites = ["setuptools", "cython>=3.1"]


recipe = Pygame261Recipe()

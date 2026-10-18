"""Pygame 2.6.1 Android recipe, with a Cython 3.1 compatibility workaround.

Pygame's optional src_c/cython/pygame/_sprite.pyx currently fails Cython
3.1's compiler ("Illegal use of special attribute __dict__"). The public
pygame.sprite Python module does not import this optional extension, so omit
only that extension from the Android build. Desktop Pygame remains unchanged.
"""
import os
from os.path import join

from pythonforandroid.recipes.pygame import Pygame2Recipe


class Pygame261Recipe(Pygame2Recipe):
    version = "2.6.1"
    url = "https://github.com/pygame/pygame/archive/{version}.tar.gz"
    hostpython_prerequisites = ["setuptools", "cython>=3.1"]

    def prebuild_arch(self, arch):
        super().prebuild_arch(arch)
        build_dir = self.get_build_dir(arch.arch)
        optional_sprite = join(build_dir, "src_c", "cython", "pygame", "_sprite.pyx")
        if os.path.exists(optional_sprite):
            os.remove(optional_sprite)


recipe = Pygame261Recipe()

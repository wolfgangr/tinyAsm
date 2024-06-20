from setuptools import setup
import sys, os

version_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 
                            "freecad", "tinyAsmWB", "version.py")
with open(version_path) as fp:
    exec(fp.read())

setup(name='freecad.tinyAsmWB',
      version=__version__,
      packages=['freecad',
                'freecad.tinyAsmWB'],
      maintainer="wolfgangr",
      maintainer_email="wolfgangr@github.com",
      url="https://github.com/wolfgangr/tinyAsmWB",
      description="tiny Assembly WB for FreeCAD",
      install_requires=[],
      include_package_data=True)

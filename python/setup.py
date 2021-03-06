from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import shutil
import subprocess

from setuptools import setup, find_packages, Distribution
import setuptools.command.build_ext as _build_ext


class build_ext(_build_ext.build_ext):
  def run(self):
    subprocess.check_call(["../build.sh"])
    # Ideally, we could include these files by putting them in a MANIFEST.in or
    # using the package_data argument to setup, but the MANIFEST.in gets
    # applied at the very beginning when setup.py runs before these files have
    # been created, so we have to move the files manually.
    for filename in files_to_include:
      self.move_file(filename)
    # Copy over the autogenerated flatbuffer Python bindings.
    generated_python_directory = "ray/core/generated"
    for filename in os.listdir(generated_python_directory):
      if filename[-3:] == ".py":
        self.move_file(os.path.join(generated_python_directory, filename))

  def move_file(self, filename):
    # TODO(rkn): This feels very brittle. It may not handle all cases. See
    # https://github.com/apache/arrow/blob/master/python/setup.py for an
    # example.
    source = filename
    destination = os.path.join(self.build_lib, filename)
    # Create the target directory if it doesn't already exist.
    parent_directory = os.path.dirname(destination)
    if not os.path.exists(parent_directory):
      os.makedirs(parent_directory)
    print("Copying {} to {}.".format(source, destination))
    shutil.copy(source, destination)


files_to_include = [
    "ray/core/src/common/thirdparty/redis/src/redis-server",
    "ray/core/src/common/redis_module/libray_redis_module.so",
    "ray/core/src/plasma/plasma_store",
    "ray/core/src/plasma/plasma_manager",
    "ray/core/src/plasma/libplasma.so",
    "ray/core/src/local_scheduler/local_scheduler",
    "ray/core/src/local_scheduler/liblocal_scheduler_library.so",
    "ray/core/src/numbuf/libnumbuf.so",
    "ray/core/src/global_scheduler/global_scheduler"
]


class BinaryDistribution(Distribution):
  def has_ext_modules(self):
    return True


setup(name="ray",
      version="0.1.0",
      packages=find_packages(),
      cmdclass={"build_ext": build_ext},
      # The BinaryDistribution argument triggers build_ext.
      distclass=BinaryDistribution,
      install_requires=["numpy",
                        "funcsigs",
                        "colorama",
                        "psutil",
                        "redis",
                        "cloudpickle >= 0.2.2",
                        "flatbuffers"],
      include_package_data=True,
      zip_safe=False,
      license="Apache 2.0")

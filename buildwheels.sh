#!/bin/bash
#
# Build manylinux wheels for HTSeq. Based on the example at
# <https://github.com/pypa/python-manylinux-demo>
#
# It is best to run this in a fresh clone of the repository!
#
# Run this within the repository root:
#   docker run --rm -v $(pwd):/io quay.io/pypa/manylinux2010_x86_64 /io/buildwheels.sh
#
# The wheels will be put into the wheelhouse/ subdirectory.
#
# For interactive tests:
#   docker run -it -v $(pwd):/io quay.io/pypa/manylinux2010_x86_64 /bin/bash

set -xeuo pipefail

# For convenience, if this script is called from outside of a docker container,
# it starts a container and runs itself inside of it.
if ! grep -q docker /proc/1/cgroup; then
  # We are not inside a container
  exec docker run --rm -v $(pwd):/io quay.io/pypa/manylinux2010_x86_64 /io/$0
fi

# Install zlib dev libraries for HTSlib when needed
# manylinux2010 is CentOS 6
yum -y install zlib-devel bzip2-devel xz-devel

# Python 2.6 is not supported
rm -rf /opt/python/cp26*
rm -rf /opt/python/cpython-2.6*

# Python 2.7 is deprecated
rm -rf /opt/python/cp27*
rm -rf /opt/python/cpython-2.7*

# Python 3.3-4 is not supported:
rm -rf /opt/python/cp33*
rm -rf /opt/python/cp34*

# Build wheels
PYBINS="/opt/python/*/bin"
for PYBIN in ${PYBINS}; do
    # Make sure the wheelbuilder has a recent cython
    ${PYBIN}/pip install Cython
    ${PYBIN}/pip install -r /io/requirements.txt
    ${PYBIN}/pip wheel /io/ -w wheelhouse/
done

# Repair HTSeq wheels, copy libraries
for whl in wheelhouse/*.whl; do
    if [[ $whl == wheelhouse/HTSeq* ]]; then
      auditwheel repair -L . $whl -w /io/wheelhouse/
    else
      cp $whl /io/wheelhouse/
    fi
done

# Created files are owned by root, so fix permissions.
chown -R --reference=/io/setup.py /io/wheelhouse/

# Build source dist
cd /io
${PYBIN}/python setup.py sdist --dist-dir /io/wheelhouse/

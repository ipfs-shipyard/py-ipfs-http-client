#!/usr/bin/python3
import os.path
from setuptools import setup, find_packages


# Make current version number as `__version__` available
__dir__     = os.path.dirname(__file__)
__version__ = None  # flake8 is being stupid
with open(os.path.join(__dir__, 'ipfsapi', 'version.py')) as file:
    exec(file.read())


setup(
    name='ipfsapi',

    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    version=__version__,

    description='IPFS API Bindings for Python',

    # The project's main homepage.
    url='https://github.com/ipfs/py-ipfs-api',

    # Author details
    author='Andrew Stocker',
    author_email='sleepyams@gmail.com',

    # Choose your license
    license='MIT',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: Science/Research',

        'Topic :: Internet',
        'Topic :: Scientific/Engineering',
        'Topic :: System :: Filesystems',
        'Topic :: System :: Networking',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],

    # What does your project relate to?
    keywords='ipfs storage distribution development',

    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    packages=find_packages(),

    # List run-time dependencies here.  These will be installed by pip when
    # your project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    install_requires=[
        'requests>=2.2.1',
        'six'
    ],

)

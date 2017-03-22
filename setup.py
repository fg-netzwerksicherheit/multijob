"""Configure, build, and install the module."""

from setuptools import setup

setup(
    name='multijob',
    packages=['multijob'],
    data_files=[
        ('', ['LICENSE']),
    ],
    setup_requires=[
        'pytest-runner',
    ],
    tests_require=[
        'pytest',
        'pytest-describe',
        'pytest-cov',
    ],
)

"""Test commandline module.

These tests handle special cases not considered by the doctests,
which are focussed on normal usage.
"""

# pylint: disable=missing-docstring,invalid-name,unused-variable

import pytest
import multiprocessor.commandline as commandline

def describe_job_from_argv():

    def it_requires_separator():

        def target(a):
            return a

        argv = ['--id=2', '--rep=0', 'a=42']
        typemap = dict(a='int')

        with pytest.raises(ValueError):
            commandline.job_from_argv(argv, target, typemap=typemap)

    def it_throws_when_meta_key_not_present():

        def target(a):
            return a

        argv = ['--', 'a=42']
        typemap = dict(a='int')

        with pytest.raises(KeyError):
            commandline.job_from_argv(argv, target, typemap=typemap)

    def it_throws_on_unexpected_meta_args():

        def target():
            pass

        argv = ['--id=4', '--rep=5', '--florbleglomp=ftaneth', '--']

        with pytest.raises(TypeError):
            commandline.job_from_argv(argv, target, typemap={})

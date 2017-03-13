============================
From scripts to GNU Parallel
============================

This tutorial describes in more detail how you can run jobs with GNU Parallel by using the :mod:`multijob.commandline` module.

Prerequisites:

- You can generate job configurations with :class:`multijob.job.JobBuilder`.

- You can run :class:`~multijob.job.Job`\ s and can deal with :class:`~multijob.job.JobResult`\ s.

- You are comfortable with the Linux shell.

Concepts and Architecture
=========================

The :mod:`multijob` module is intended to support
easy parallelization of computation-intensive jobs,
for example: evolutionary algorithms.
We assume all jobs are the same
but are executed with different parameter values.

For the purpose of this tutorial, we will assume the EA is written in Python.
However, the command line interface is language-agnostic and can also be adapted for other languages.

The central part of your work is the executable that performs the job.
I'll call it ``runGA.py``.
This executable will be invoked with the job parameters as command line parameters.
The command line parameters are represented in our code as :class:`multijob.job.Job` objects.

The general workflow is:

1.  Generate a list of job configurations with the :class:`multijob.job.JobBuilder`.
2.  Turn the list into a shell script with :func:`multijob.command.shell_command_from_job`.
    This shell script can be seen as a job queue.
3.  Process the job queue with GNU Parallel.
    This will invoke the ``runGA.py`` program.
    The actual target program may be run locally, or on a remote server.
4.  In the ``runGA.py``, decode the command line arguments back to a Job instance.
5.  In the ``runGA.py``, execute the Job
6.  In the ``runGA.py``, write the results to output files.
7.  Aggregate and analyze your results.

Typemaps and Coercions
======================

To convert between :class:`multijob.job.Job` instances and command line parameters, we need to *coerce* each parameter value.
A :class:`~multijob.commandline.Coercion` is a function that specifies how this is done.
A mapping between parameter names and the coercions that should be used for these parameters is a *typemap*.

When converting a job to the command line params, by default we convert each parameter with ``str()``.
This works fine for strings, numbers, booleans, etc.::

    >>> from multijob.job import JobBuilder
    >>> from multijob.commandline import shell_command_from_job
    >>> def dummy_target(x, y, z):
    ...     pass
    ...
    >>> job, *_ = JobBuilder(x='foo', y=42.3, z=False).build(dummy_target)
    >>> print(shell_command_from_job('runGA.py', job))
    runGA.py --id=0 --rep=0 -- x=foo y=42.3 z=False

If you want to pass special types that do not have a suitable string representation, you may have to write your own coercion.
E.g. if you want to pass a list of values for a parameter, we might want to encode it as CSV.
Note that we now declare a ``TYPEMAP``:

    >>> import csv, io
    >>> from multijob.job import JobBuilder
    >>> from multijob.commandline import shell_command_from_job
    >>> def dummy_target(xs):
    ...     pass
    ...
    >>> def as_csv_line(values):
    ...     out = io.StringIO()
    ...     csv.writer(out).writerow(values)
    ...     return out.getvalue().strip('\r\n')
    ...
    >>> TYPEMAP = dict(xs=as_csv_line)
    >>> job, *_ = JobBuilder(xs=['Bond, James', '007']).build(dummy_target)
    >>> print(shell_command_from_job('runGA.py', job, typemap=TYPEMAP))
    runGA.py --id=0 --rep=0 -- 'xs="Bond, James",007'

This typemap just says:
“for the ``xs`` parameter, use the ``as_csv_line()`` function.”

On the other end, we have to turn the command line parameters back to into a Job instance.
This is usually a bit more difficult.
In particular, we will almost always need a typemap.
The coercions now specify how to turn the string back into a Python object.
For simple built-in types like strings, ints, floats, and bools, you can use the type name as a string in place of a coercion – a *named coercion*.
See the :class:`~multijob.commandline.Coercion` docs for details.

In Python, the command line parameters can be read from the ``sys.argv`` list.
The first item is the name of the current command and has to be skipped.
Multijob provides the :func:`multi.commandline.job_from_argv` function for the conversion::

    >>> from multijob.commandline import job_from_argv
    >>> def my_algorithm(x, y, z):
    ...     ...  # you probably have something more interesting here
    ...     return y if z else len(x)
    ...
    >>> TYPEMAP = dict(
    ...     x='str',
    ...     y='float',
    ...     z='bool',
    ... )
    ...
    >>> # argv = sys.argv
    >>> argv = ['runGA.py', '--id=0', '--rep=0', '--',
    ...         'x=foo', 'y=42.3', 'z=False']
    >>> # remember to skip first argv entry
    >>> job = job_from_argv(argv[1:], my_algorithm, typemap=TYPEMAP)
    ...
    >>> # execute the job
    >>> res = job.run()
    >>> res.result
    3

Instead of using the predefined named coercions, you can always provide your own functions.

Converting a ``runGA()`` function to a ``runGA.py`` script
==========================================================

TODO

Creating the jobs
=================

TODO

Turning jobs into shell commands
================================

TODO

Executing jobs with ``parallel``
================================

TODO

Suggested workflow and conventions
==================================

TODO

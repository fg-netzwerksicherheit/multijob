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
2.  Turn the list into a shell script with :func:`multijob.commandline.shell_command_from_job`.
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

When moving to Multijob, you don't have to throw your existing code away:
Multijob is absolutely framework-agnostic.
We only need a function that takes all configuration parameters as (named) arguments.
So as long as you have such a ``runGA()`` function or can easily write one, everything is good.

In Python, it is possible to use a ``.py`` file as both a module that can be imported, and a script that can be executed directly.
Anything that should be only run for a script has to be guarded, since top-level code is executed even for modules::

    ... # always executed

    if __name__ == '__main__':
        ... # only executed when used as a script

The ``runGA()`` function would be in the always-executed part.
Our adaption code will live in the guarded section.

To adapt this function, we only have to decode the command line parameters.
As shown above, this requires a *typemap*.
We then get a :class:`~multijob.job.Job` instance that can then be run.

To construct the typemap, we look at the parameters for the ``runGA`` function.
Usually, our typemap will have an entry for each named parameter.
Here is a simple case::

    def runGA(popsize, cxpb, mutpb, use_injection):
        ...

All parameters are named in the function definition, so we start writing our typemap::

    TYPEMAP = dict(
        popsize=...,
        cxpb=...,
        mutpb=...,
        use_injection=...)

We now have to select the types for these parameters.
Note that the typemap does not contain classes or class names, but *coercion functions* that parse the parameter value from a string.
Some constructors (like :func:`int`) happen to correctly parse any string they are given.
For other constructors, this is not the case.
For example, ``bool('False') == True``, so :func:`bool` *is not* a suitable coercion function.

To solve such problems, common conversions can simply be specified as *named coercions*. Here::

    TYPEMAP = dict(
        popsize='int',
        cxpb='float',
        mutpb='float',
        use_injection='bool')

Not all functions are so easy.
If the parameter list uses ``**kwargs`` to collect many named parameters, you'll have to trace the code to find the actual parameter names.
If the parameter list slurps many ``*args`` into a list, you will have to provide a parameter called ``args`` in your TYPEMAP which then expects a list.
Remember that all parameters are passed as named parameters, not as positional parameters.

With the typemap, you can easily re-create a job from the command line arguments and execute it::

    import sys
    from multijob.commandline import job_from_argv

    def runGA(a, b, c):
        ...

    TYPEMAP = dict(a=..., b=..., c=...)

    if __name__ == '__main__':
        job = job_from_argv(sys.argv[1:], runGA, typemap=TYPEMAP)
        res = job.run()
        ...

Note that you have to skip the first command line parameter:
``sys.argv[0]`` contains the name of the executable, not any real parameters.

After you executed the job,
the :class:`~multijob.job.JobResult` should be stored somewhere.
It is best to use language-agnostic formats like CSV for this.

If you are storing the results in a file, you will of course need different file names for each parameter configuration.
The Job object includes :attr:`~multijob.job.Job.job_id` and :attr:`~multijob.job.Job.repetition_id` properties that can be used here.
The :attr:`~multijob.job.Job.job_id` identifies the parameter configuration.
If you repeated each configuration, the ``job_id`` is therefore not unique.
Instead, the :attr:`~multijob.job.Job.repetition_id` identifies repetitions of the same `job_id`.

To create a result file using both of these IDs, you could do::

    filename = "results.{}.{}.csv".format(job.job_id, job.repetition_id)
    with open(filename, 'w') as f:
        ...

This produces file names like ``results.3.7.csv``.

Of course, Multijob imposes no restrictions on the file name so you can use whatever schema you want, or even use non-file-based solutions like REST APIs or databases.

In my experience, it is best to put all of this plumbing into a separate ``main()`` function. For example::

    import sys
    from multijob.commandline import job_from_argv

    def runGA(...):
        ...

    TYPEMAP = dict(...)

    def main(argv):
        job = job_from_argv(argv, runGA, typemap=TYPEMAP)
        res = job.run()

        filename = "results-{}-{}-logbook.csv".format(
            job.job_id, job.repetition_id)
        with open(filename, 'w') as f:
            csv_file = csv.writer(f)
            for record in res.result:
                csv_file.writerow(record)

    if __name__ == '__main__':
        main(sys.argv[1:])

Now that your actual algorithm has been wrapped as an independent shell script,
you can test it by running the script directly.
Remember that you will have to provide all parameters in the expected format, and that you have to provide a job id::

    $ python runGA.py --id=0 --rep=0 -- x=7 y=42.3 z='foo bar'

Creating the jobs
=================

The :class:`multijob.job.JobBuilder` is used to generate all job configurations you want to run.
For each parameter, you can specify a list of one or more possible values for this parameter.
The job configurations are then the cartesian product of these lists.

You have multiple possibilities to provide these lists:

-   :meth:`builder.add(name, *values) <multijob.job.JobBuilder.add>`
    – explicitly provide the values. Recommended.
-   :meth:`builder.add_range(name, start, stop, stride) <multijob.job.JobBuilder.add_range>`
    – add a list of floats, starting from the ``start``, where the ``stride`` separates two consecutive numbers.
-   :meth:`builder.add_linspace(name, start, stop, n) <multijob.job.JobBuilder.add_linspace>`
    – add a list of ``n`` evenly spaced floats
    including the ``start`` and ``stop``.

Example::

    >>> from multijob.job import JobBuilder
    >>> builder = JobBuilder()
    >>> builder.add('explict', 1, 2, 3)
    (1, 2, 3)
    >>> builder.add_range('range', 0.0, 6.0, 2.0)
    [0.0, 2.0, 4.0, 6.0]
    >>> builder.add_linspace('linspace', 3.0, 6.0, 4)
    [3.0, 4.0, 5.0, 6.0]

The ``add_range()`` and ``add_linspace()`` variants are only convenience functions.
They have many problematic aspects:

-   They only operate on floats.
    Because floats are inherently imprecise, you may see rounding problems.

-   Also, their output is evenly spaced.
    Your parameters might benefit from a different distribution, e.g. more dense around zero, or selected randomly.
    Randomizing your values also prevents sampling artifacts.
    If you randomize your values, make sure to record the random generator seed to ensure reproducibility!

When you specify many possible parameter values, this easily leads to a combinatorial explosion of job configurations.
You may want to check for a sane number of configurations first.
For that each builder can calculate the expected :meth:`~multijob.job.Job.number_of_jobs`.
This only considers the number of distinct configurations that will be built, but does not consider repetitions.

::

    n_jobs = builder.number_of_jobs()
    max_jobs = 1000
    if n_jobs > max_jobs:
        raise RuntimeError(
            "too many job configurations: {}/{}".format(n_jobs, max_jobs))

Finally, we generate the actual list of jobs.
Since we want to turn the jobs into shell commands,
these job instances will never be directly run.
We can therefore use a dummy callback for the worker function::

    def dummy(**kwargs):
        pass

    jobs = builder.build(dummy)

For many uses, it makes sense to repeat each configuration multiple times.
In the context of evolutionary algorithms, the results of a single run are not statistically significant.
We need multiple repetitions of each configuration in order to draw reliable conclusions.
The ``build()`` method can take a ``repetitions`` argument that specifies the number of repetitions of each config, it defaults to 1.

The repeated job objects are identical (same param values, same job id) except for the repetition ID.

::

    jobs = builder.build(dummy, repetitions=20)

Turning jobs into shell commands
================================

TODO

Executing jobs with ``parallel``
================================

TODO

Suggested workflow and conventions
==================================

TODO

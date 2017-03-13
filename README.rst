==========================================================================
Multijob – define multiple job configurations and execute them in parallel
==========================================================================

When you have a job that you need to run many times in many configurations – this module is the solution.

Job parameters
==============

(see :mod:`multijob.job`)

Generating a matrix of value combinations either involves many nested loops,
or the :class:`multijob.job.JobBuilder`::

    >>> from multijob.job import JobBuilder
    >>> builder = JobBuilder()
    >>> # add one or more specific parameters
    >>> builder.add('param', True, False)
    (True, False)
    >>> # add a range of floats
    >>> builder.add_range('x', 0, 10, 2.5)
    [0.0, 2.5, 5.0, 7.5, 10.0]
    >>> # add a range of floats with a specific number of elements
    >>> builder.add_linspace('y', 0, 1, 5)
    [0.0, 0.25, 0.5, 0.75, 1.0]
    >>> # how many jobs will we get?
    >>> builder.number_of_jobs()
    50
    >>> # actually generate all the jobs
    >>> def worker(param, x, y):
    ...     print(x + y if param else None)
    >>> jobs = builder.build(worker)
    >>> jobs
    [<multijob.job.Job object at 0x...>, ...]
    >>> # execute the jobs (invokes the function with all parameters):
    >>> for job in jobs:  # doctest: +NORMALIZE_WHITESPACE
    ...     _ = job.run()
    0.0 ... 11.0 ... None

Execute jobs with `multiprocessing`
===================================

TODO

Execute jobs with GNU Parallel
==============================

(see :mod:`multijob.commandline`)

`GNU Parallel <https://www.gnu.org/software/parallel/>`_ is a sophisticated command-line tool for running many processes in parallel.
The :mod:`multijob.commandline` module allows us to represent jobs as command line arguments, so that a job list can be managed by GNU Parallel.
Main advantages of this approach are:

- The worker function and the job definitions don't have to be in the same language. Build the jobs in Python, run them in Go, C++, or any other language!
- Jobs can be distributed over multiple servers via SSH!
- Get an ETA for job completion!
- Restart aborted or failed jobs!

We can turn a job into a shell command with :func:`multijob.commandline.shell_command_from_job`. These commands would usually be written to a file like ``jobs.sh``::

    >>> from multijob.job import JobBuilder
    >>> from multijob.commandline import shell_command_from_job
    >>> builder = JobBuilder()
    >>> _ = builder.add('a', 'x', 'y')
    >>> _ = builder.add('b', 1, 2, 3)
    >>> jobs = builder.build(lambda **_: None)  # ignore worker function
    >>> for job in jobs:
    ...     print(shell_command_from_job('$JOB_TARGET', job))
    $JOB_TARGET --id=0 --rep=0 -- a=x b=1
    $JOB_TARGET --id=1 --rep=0 -- a=x b=2
    $JOB_TARGET --id=2 --rep=0 -- a=x b=3
    $JOB_TARGET --id=3 --rep=0 -- a=y b=1
    $JOB_TARGET --id=4 --rep=0 -- a=y b=2
    $JOB_TARGET --id=5 --rep=0 -- a=y b=3

By default, the job parameters are rendered on the command line via :func:`str`, but this can be adapted by a *typemap* when necessary.

In the above example, we used a shell variable ``$JOB_TARGET`` as command to invoke with these args. That way, it can be provided later, adding extra flexibility. For example::

    $ JOB_TARGET='python worker.py' parallel <jobs.sh

There are many options to Parallel.
I recommend looking at least at the following items in the docs (`man parallel <https://www.gnu.org/software/parallel/man.html>`_):

- ``--eta`` gives an estimated time of completion for all scheduled jobs.
- ``--jobs N`` limits the number of concurrent jobs – good for testing.
- ``--joblog FILE`` logs completed jobs. Necessary to resume a batch later.
- ``--line-buffer`` intermingles the STDOUT/STDERR output of all jobs. Improves performance in some cases.

Now that we have the command line args, how do we turn them back into Job?
For Python, :mod:`multijob.commandline.job_from_argv` can recreate a Job object from these arguments.

First, we have to create a *typemap* that describes which argument has which type. The typemap contains coercion functions that parse that type from a string. As a shortcut, simple types can be named. See :class:`multijob.commandline.Coercion` for details. Here::

    TYPEMAP = dict(a='str', b='int')

Then we only need a worker function, and can recreate the job::

    >>> from multijob.commandline import job_from_argv
    >>> # argv = sys.argv
    >>> argv = ['worker.py', '--id=1', '--rep=0', '--', 'a=x', 'b=1']
    >>> argv = argv[1:]  # skip 1st argument
    >>> # typemap and worker function
    >>> TYPEMAP = dict(a='str', b='int')
    >>> def worker(a, b):
    ...     return [a, b]
    >>> # recreate and run the job
    >>> job = job_from_argv(argv, worker, typemap=TYPEMAP)
    >>> print(job)
    1:0: a='x' b=1
    >>> result = job.run()
    >>> result.result
    ['x', 1]

Typically, you'd then write the result to a file, using the job's :attr:`~multijob.job.Job.job_id` and :attr:`~multijob.job.Job.repetition_id` to construct the filename.

For the example of evolutionary algorithms, this is discussed in more detail int the :doc:`parallelTutorial` tutorial.

Corresponding command line argument parsers for other languages may be implemented in the future.

Authors
=======

-   Robin Müller-Bady
-   Lukas Atkinson

http://netzwerksicherheit.fb2.fh-frankfurt.de/

Copyright and License
=====================

Copyright 2017 Frankfurt University of Applied Sciences


Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

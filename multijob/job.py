# coding: utf8

"""Job configurations

.. autosummary::
    Job
    JobBuilder
    JobResult

"""

import itertools

class Job(object):
    """A concrete set of configuration parameters.

    Args:
        job_id: identify this set of parameters
        repetition_id: distinguish repetitions of this set of parameters
        callback: function to invoke with params
        params (dict): the parameters
    """

    def __init__(self, job_id, repetition_id, callback, params):
        self._job_id = job_id
        self._repetition_id = repetition_id
        self._callback = callback
        self._params = params

    @property
    def job_id(self):
        """Identifies this set of parameters"""
        return self._job_id

    @property
    def repetition_id(self):
        """Distinguishes repetitions of this set of parameters."""
        return self._repetition_id

    def run(self):
        """Execute the job.

        Returns:
            JobResult: the callback result, wrapped in a :class:`JobResult`.

        Example::

            >>> def add(x, y): return x + y
            >>> job = Job(1, 2, add, dict(x=2, y=40))
            >>> result = job.run()
            >>> result.job is job
            True
            >>> result.result
            42
        """
        result = self._callback(**self.params)
        return JobResult(self, result)

    @property
    def params(self):
        """dict: The chosen set of parameters. Do not modify."""
        return self._params

    def __str__(self):
        job_id = self.job_id
        repetition_id = self.repetition_id
        params = self.params

        formatted_params = ' '.join(
            '{}={!r}'.format(key, params[key])
            for key in sorted(params.keys())
        )

        return '{}:{}: {}'.format(job_id, repetition_id, formatted_params)

class JobResult(object):
    """The result of a job execution."""

    def __init__(self, job, result):
        self._job = job
        self._result = result

    @property
    def job(self):
        """Job: The job that was run to generate this result."""
        return self._job

    @property
    def result(self):
        """Whatever the job callback returned."""
        return self._result

class JobBuilder(object):
    """Create a range of jobs to cover the required parameter combinations

    Args:
        defaults: any default values for the parameters
    """

    def __init__(self, **defaults):
        self._param_lists = {}

        for param, value in defaults.items():
            self.add(param, value)

    def _add_list(self, param, values):
        if param in self._param_lists:
            raise RuntimeError("redefinition of parameter {!r}".format(param))
        self._param_lists[param] = list(values)


    def add(self, param, *values):
        """Add a specific range of parameters.

        Args:
            param: the name of the parameter
            values: The values you want to add

        Returns:
            The added values.

        Example::

            >>> builder = JobBuilder()
            >>> builder.add('x', 1, 2, 3)
            (1, 2, 3)

        Example: Redefinition of a parameter is impossible::

            >>> builder = JobBuilder()
            >>> builder.add('x', 1, 2, 3)
            (1, 2, 3)
            >>> builder.add('x', 4, 5, 6)
            Traceback (most recent call last):
            RuntimeError: redefinition of parameter 'x'
        """
        self._add_list(param, values)
        return values

    def add_range(self, param, start, end, stride):
        """Create a ``[start, end]`` *inclusive* range of floats.

        Args:
            param (str):
                The name of the param to add.
            start (float):
                The start of the range.
            end (float):
                The inclusive end of the range. This might not be included if
                ``(end - start)/stride`` is not integer.
            stride (float):
                The step size between numbers in the range.

        Returns:
            The added values.

        Example::

            >>> builder = JobBuilder()
            >>> builder.add_range('x', 0, 3, 0.5)
            [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0]

        Example: start must be smaller than end::

            >>> builder = JobBuilder()
            >>> builder.add_range('x', 3, 0, 0.5)
            Traceback (most recent call last):
            ValueError: start must be smaller than end

        Example: stride must be positive::

            >>> builder = JobBuilder()
            >>> builder.add_range('x', 0, 3, -0.5)
            Traceback (most recent call last):
            ValueError: stride must be positive

        """

        if not start < end:
            raise ValueError("start must be smaller than end")

        if stride <= 0:
            raise ValueError("stride must be positive")

        def _values():
            # pylint: disable=invalid-name
            n = 0
            while True:
                value = start + n * stride
                if value <= end:
                    yield value
                else:
                    break
                n += 1

        values = list(_values())

        self._add_list(param, values)
        return values

    def add_linspace(self, param, start, stop, num):
        """ Create a ``[start, stop]`` *inclusive* range of floats.

        Args:
            param (str):
                The name of the param to add.
            start (float):
                The start of the range.
            stop (float):
                The inclusive stop of the range.
            num (int):
                The number of items in the range, must be at least 2.

        Returns:
            The added items.

        Example::

            >>> builder = JobBuilder()
            >>> builder.add_linspace('x', 0, 3, 7)
            [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0]

        Example: start must be smaller than stop::

            >>> builder = JobBuilder()
            >>> builder.add_linspace('x', 3, 0, 7)
            Traceback (most recent call last):
            ValueError: start must be smaller than stop

        Example: num must be at least 2 to include start and stop:

            >>> builder = JobBuilder()
            >>> builder.add_linspace('x', 0, 3, 1)
            Traceback (most recent call last):
            ValueError: num must be at least 2 to include the start and stop

        """

        if not start < stop:
            raise ValueError("start must be smaller than stop")

        if num < 2:
            raise ValueError("num must be at least 2 to include the start and stop")

        span = stop - start
        stride = span / (num - 1)
        values = [start + n * stride for n in range(num)]

        self._add_list(param, values)
        return values

    def number_of_jobs(self):
        """Calculate the number of jobs that will be generated.

        Example::

            >>> builder = JobBuilder()
            >>> builder.number_of_jobs()
            1
            >>> builder.add('a', 7)
            (...)
            >>> builder.add('b', 1, 2, 3)
            (...)
            >>> builder.add('c', 'a', 'b', 'c', 'd')
            (...)
            >>> builder.number_of_jobs()
            12
        """

        num = 1
        for values in self._param_lists.values():
            num *= len(values)
        return num

    def build(self, callback, repetitions=1):
        """Create all Job objects from this configuration.

        Args:
            callback: The function to invoke in the Job.
            repetitions: How often each parameter set should be repeated.

        Returns:
            List[Job]: All job objects.

        Example::

            >>> def target(x, y, z): pass
            >>> builder = JobBuilder(x=2)
            >>> builder.add('y', 1, 2, 3)
            (...)
            >>> builder.add('z', True, False)
            (...)
            >>> jobs = builder.build(target, 2)
            >>> jobs
            [<multijob.job.Job object at 0x...>, ...]
            >>> for job in jobs:
            ...     print(job)
            0:0: x=2 y=1 z=True
            0:1: x=2 y=1 z=True
            1:0: x=2 y=1 z=False
            1:1: x=2 y=1 z=False
            2:0: x=2 y=2 z=True
            2:1: x=2 y=2 z=True
            3:0: x=2 y=2 z=False
            3:1: x=2 y=2 z=False
            4:0: x=2 y=3 z=True
            4:1: x=2 y=3 z=True
            5:0: x=2 y=3 z=False
            5:1: x=2 y=3 z=False

        Example: empty config still produces a configuration::

            >>> def target(): pass
            >>> builder = JobBuilder()
            >>> builder.build(target, 2)
            [<...>, <...>]

        Example: the callback must be callable::

            >>> builder = JobBuilder()
            >>> builder.build("target", 2)
            Traceback (most recent call last):
            TypeError: callback must be callable

        Example: at least one repetition required::

            >>> def target(): pass
            >>> builder = JobBuilder()
            >>> builder.build(target, 0)
            Traceback (most recent call last):
            ValueError: at least one repetition required

        """

        if not callable(callback):
            raise TypeError("callback must be callable")

        if repetitions < 1:
            raise ValueError("at least one repetition required")

        params_as_dict_of_lists = self._param_lists
        params_as_lists_of_pairs = [
            [(key, value) for value in params_as_dict_of_lists[key]]
            for key in sorted(params_as_dict_of_lists.keys())
        ]
        params_product = [
            dict(kv_pairs)
            for kv_pairs in itertools.product(*params_as_lists_of_pairs)
        ]

        jobs = []

        for job_id, params in enumerate(params_product):
            for repetition_id in range(repetitions):
                jobs.append(Job(job_id, repetition_id, callback, params))

        return jobs

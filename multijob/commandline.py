# coding: utf8

"""Turn job objects into command line arguments and back again.

You should use :func:`job_from_argv` and :func:`argv_from_job` to convert
between :class:`multijob.job.Job` instances and command line parameters.  These
functions use *typemaps* and *coercions*.

A typemap is a dictionary that maps named params to a specific coercion.

A coercion is a function that turns a string into a Python data type or back
(see :class:`Coercion`).

If you need to take more control over parsing, you can get convenient
random-access to the command line parameters via :class:`UnparsedArguments`, or
can apply a particular coercion to a string value via
:func:`value_from_string`.

.. class:: Coercion

    Coercion from command line args to Python objects.

    Coercions describe how command line arguments are converted to Python data
    types. There isn't an actual coercion class, but this concept is used
    throughout the module documentation.

    Coercions are functions that take a single parameter (the string to be
    coerced) and return a single Python object.  Coercions may also be *named*.
    Instead of supplying a callback, the coercion may be one of:

    -   ``'str'``
    -   ``'int'``
    -   ``'float'``
    -   ``'bool'``

"""

import multijob.job

def _parse_bool(value):
    """Parse a boolean string "True" or "False".

    Example::

        >>> _parse_bool("True")
        True
        >>> _parse_bool("False")
        False
        >>> _parse_bool("glorp")
        Traceback (most recent call last):
        ValueError: Expected 'True' or 'False' but got 'glorp'
    """

    if value == 'True':
        return True
    if value == 'False':
        return False
    raise ValueError("Expected 'True' or 'False' but got {!r}".format(value))

NAMED_COERCIONS = dict(
    str=str,
    int=int,
    float=float,
    bool=_parse_bool,
)

def _update_ex_message(ex, new_message, *args, **kwargs):
    """Given an exception, prepend something to its message.

    Example::

        >>> ex = TypeError("bad type")
        >>> _update_ex_message(ex, "caught with x={}:", 42)
        >>> raise ex
        Traceback (most recent call last):
        TypeError: caught with x=42:
        bad type

    """

    new_message = new_message.format(*args, **kwargs)
    ex.args = (new_message + "\n" + ex.args[0], *ex.args[1:])

def value_from_string(name, value, coercion):
    """Parse a value from a string with a given coercion.

    This function primarily adds error handling,
    and contains support for named coercions.

    Args:
        name (str): The name of this argument, needed for diagnostics.
        value (str): The string to coerce.
        coercion (str|Coercion): a named coercion or a coercion callback.

    Returns:
        the coerced value.

    Example: normal usage::

        >>> value_from_string('x', '42', int)
        42

    Example: requires a coercion::

        >>> value_from_string('x', '42', None)
        Traceback (most recent call last):
        TypeError: no coercion found for 'x'='42'

    Example: named coercions::

        >>> value_from_string('x', 'False', 'bool')
        False

    Example: coercions must be callable::

        >>> value_from_string('x', '42', 123)
        Traceback (most recent call last):
        TypeError: 'x' coercion must be callable: 123

    Example: reports error when coercion failed::

        >>> def bad_coercion(value):
        ...     raise ValueError("nope")
        ...
        >>> value_from_string('x', '42', bad_coercion)
        Traceback (most recent call last):
        ValueError: Could not coerce 'x'='42':
        nope
    """

    if coercion is None:
        raise TypeError("no coercion found for {!r}={!r}".format(name, value))

    if isinstance(coercion, str):
        coercion = NAMED_COERCIONS[coercion]

    if not callable(coercion):
        raise TypeError(
            "{!r} coercion must be callable: {!r}".format(name, coercion),
        )

    try:
        return coercion(value)
    except ValueError as ex:
        _update_ex_message(ex, "Could not coerce {!r}={!r}:", name, value)
        raise

def _string_from_value(name, value, coercion):
    """Turn a value into a string, optionally with a given coercion.

    Example: normal usage::

        >>> _string_from_value('x', 42, str)
        '42'

    Example: coercion defaults to str::

        >>> _string_from_value('x', 42, None)
        '42'

    Example: coercion must be callable::

        >>> _string_from_value('x', 42, 'int')
        Traceback (most recent call last):
        TypeError: 'x' coercion must be callable: 'int'

    Example: reports error when coercion failed::

        >>> class EvilValue(object):
        ...     def __str__(self):
        ...         raise ValueError("I don't want to go!")
        ...
        >>> _string_from_value('x', EvilValue(), str)
        Traceback (most recent call last):
        ValueError: Could not coerce 'x'=<multijob.commandline.EvilValue object at 0x...>:
        I don't want to go!

    """

    if coercion is None:
        coercion = str

    if not callable(coercion):
        raise TypeError(
            "{!r} coercion must be callable: {!r}".format(name, coercion)
        )

    try:
        return coercion(value)
    except ValueError as ex:
        _update_ex_message(ex, "Could not coerce {!r}={!r}:", name, value)
        raise

def _unparsed_dict_from_argv(argv):
    """Split command line arguments into a dict, without applying coercions.
    """
    arg_dict = dict()

    for arg in argv:
        name, value = arg.split('=', 1)
        arg_dict[name] = value

    return arg_dict

class UnparsedArguments(object):
    """A collection of unnamed arguments.

    This may be useful if you have to do some parsing manually.

    Use :meth:`from_argv` to construct this object from an argv array.

    Args:
        args (dict): the name-value command line parameters.
    """

    def __init__(self, args):
        self._args = dict(args)

    @staticmethod
    def from_argv(argv):
        """Create UnparsedArguments from an argv array.
        """

        return UnparsedArguments(_unparsed_dict_from_argv(argv))

    def read(self, name, coercion):
        """Consume and coerce a named argument.

        Since the argument is consumed, it cannot be consumed again.

        Args:
            name (str): The name of the argument to consume.
            coercion (Coercion): The coercion to apply to this value.

        Returns:
            the coerced value.

        Raises:
            KeyError: when no such argument name exists.
            ValueError: when the value can't be coerced.
        """

        try:
            value = self._args.pop(name)
        except KeyError:
            raise KeyError("expected {!r} in argv".format(name))

        return value_from_string(name, value, coercion)

    def __bool__(self):
        return bool(self._args)

    def __iter__(self):
        return iter(self._args)


def _dict_from_argv(argv, *, typemap, default_coercion=None):
    """Parse command line args to a dict.

    Example::

        >>> argv = ['a=42', 'b=True', 'c=foo=bar', 'd=42']
        >>> TYPEMAP = dict(a='int', b='bool', c='str', d='str')
        >>> argd = _dict_from_argv(argv, typemap=TYPEMAP)
        >>> for name in sorted(argd.keys()):
        ...     value = argd[name]
        ...     typename = type(value).__name__
        ...     print("{}: {} = {!r}".format(name, typename, value))
        a: int = 42
        b: bool = True
        c: str = 'foo=bar'
        d: str = '42'
    """

    arg_dict = dict()

    unparsed = UnparsedArguments.from_argv(argv)
    for name in list(unparsed):
        coercion = typemap.get(name, default_coercion)
        value = unparsed.read(name, coercion)
        arg_dict[name] = value

    return arg_dict

def _argv_from_dict(arg_dict, *, typemap=None, default_coercion=None):
    """Format a dict as command line args.

    Example::

        >>> argd = dict(a=42, b=True, c='foo=bar', d='42')
        >>> _argv_from_dict(argd)
        ['a=42', 'b=True', 'c=foo=bar', 'd=42']
    """

    if typemap is None:
        typemap = {}

    argv = []

    for name in sorted(arg_dict):
        value = arg_dict[name]
        coercion = typemap.get(name, default_coercion)
        coerced_value = _string_from_value(name, value, coercion)
        argv.append("{}={}".format(name, coerced_value))

    return argv

def argv_from_job(job, *, typemap=None, default_coercion=None):
    r"""Format a job as command line arguments.

    To get a job object back from these arguments,
    use :func:`job_from_argv`.

    The ``job.callback`` will not be stored
    and will have to be provided explicitly when parsing the arguments.

    Args:
        job (multijob.job):
            The job to format.
        typemap (Typemap):
            Optional. Controls how individual params are formatted.
        default_coercion (Coercion):
            Optional. Controls how params without a typemap entry are formatted.

    Returns:
        list: The encoded params.

    Example: simple usage::

        >>> from multijob.job import Job
        >>> def target(): pass
        >>> job = Job(42, 3, target, dict(a=42, b=True, c='foo'))
        >>> argv_from_job(job)
        ['--id=42', '--rep=3', '--', 'a=42', 'b=True', 'c=foo']

    Example: storing a list::

        >>> from multijob.job import Job
        >>> import csv
        >>> import io
        >>> def csv_line(items):
        ...     out = io.StringIO()
        ...     csv.writer(out).writerow(items)
        ...     return out.getvalue().strip('\r\n')
        >>> def target():
        ...     pass
        >>> job = Job(3, 0, target, dict(xs=[1, 2, 3]))
        >>> argv_from_job(job, typemap=dict(xs=csv_line))
        [..., '--', 'xs=1,2,3']

    """

    argv = []
    argv.append('--id=' + _string_from_value('--id', job.job_id, None))
    argv.append('--rep=' + _string_from_value('--rep', job.repetition_id, None))
    argv.append('--')
    argv.extend(_argv_from_dict(job.params,
                                typemap=typemap,
                                default_coercion=default_coercion))

    return argv

def job_from_argv(argv, callback, *, typemap, default_coercion=None):
    """Parse command line arguments into a job object.

    Args:
        argv (list):
            The arguments.
        callback (callable):
            A function to invoke with the params,
            see :class:`multijob.job.Job` for details.
        typemap (Typemap):
            Controls how individual params are parsed.
        default_coercion (Coercion):
            Optional. Controls how params without a typemap entry are formatted.

    Returns:
        multijob.job.Job: a runnable job with the params from this argv.

    Example: simple usage::

        >>> def target(a, b, c):
        ...     print("Args: a={!r}, b={!r}, c={!r}".format(a, b, c))
        ...     return "some value"
        ...
        >>> argv = ['--id=42', '--rep=3', '--', 'a=42', 'b=True', 'c=foo']
        >>> TYPEMAP = dict(a='int', b='bool', c='str')
        >>> job = job_from_argv(argv, target, typemap=TYPEMAP)
        >>> (job.job_id, job.repetition_id)
        (42, 3)
        >>> result = job.run()
        Args: a=42, b=True, c='foo'
        >>> result
        <multijob.job.JobResult object at 0x...>

    Example: reading a list::

        >>> import csv
        >>> def target():
        ...     pass
        >>> def csv_line(line):
        ...     return [float(x) for x in list(csv.reader([line]))[0]]
        >>> argv = ['--id=3', '--rep=14', '--', 'xs=1.2,3.4,5.6']
        >>> job = job_from_argv(argv, target, typemap=dict(xs=csv_line))
        >>> job.params['xs']
        [1.2, 3.4, 5.6]
    """

    try:
        separator_ix = argv.index('--')
    except ValueError:
        raise ValueError("no argument separator '--' found")

    meta_args = argv[:separator_ix]
    param_args = argv[separator_ix + 1:]

    raw_meta = UnparsedArguments.from_argv(meta_args)

    job_id = raw_meta.read('--id', int)
    repetition_id = raw_meta.read('--rep', int)

    if raw_meta:
        keys = sorted(raw_meta)
        raise TypeError("unexpected meta args: {}".format(', '.join(keys)))

    params = _dict_from_argv(param_args,
                             typemap=typemap,
                             default_coercion=default_coercion)

    return multijob.job.Job(job_id, repetition_id, callback, params)

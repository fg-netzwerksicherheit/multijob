# coding: utf8

"""Turn job objects into command line arguments and back again.
"""

import multiprocessor.job

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
"""
Available named coercions from strings to data types:

 -  str
 -  int
 -  float
 -  bool
"""

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

def _value_from_string(name, value, coercion):
    """Parse a value from a string with a given coercion.

    This function primarily adds error handling,
    and contains support for named coercions.

    Example: normal usage::

        >>> _value_from_string('x', '42', int)
        42

    Example: requires a coercion::

        >>> _value_from_string('x', '42', None)
        Traceback (most recent call last):
        TypeError: no coercion found for 'x'='42'

    Example: named coercions::

        >>> _value_from_string('x', 'False', 'bool')
        False

    Example: coercions must be callable::

        >>> _value_from_string('x', '42', 123)
        Traceback (most recent call last):
        TypeError: 'x' coercion must be callable: 123

    Example: reports error when coercion failed::

        >>> def bad_coercion(value):
        ...     raise ValueError("nope")
        ...
        >>> _value_from_string('x', '42', bad_coercion)
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
        ValueError: Could not coerce 'x'=<multiprocessor.commandline.EvilValue object at 0x...>:
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

    for arg in argv:
        name, value = arg.split('=', 1)
        coercion = typemap.get(name, default_coercion)
        coerced_value = _value_from_string(name, value, coercion)
        arg_dict[name] = coerced_value

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
        job (multiprocessor.job):
            The job to format.
        typemap (Typemap):
            Optional. Controls how individual params are formatted.
        default_coercion (Coercion):
            Optional. Controls how params without a typemap entry are formatted.

    Returns:
        list: The encoded params.

    Example: simple usage::

        >>> from multiprocessor.job import Job
        >>> def target(): pass
        >>> job = Job(42, 3, target, dict(a=42, b=True, c='foo'))
        >>> argv_from_job(job)
        ['--id=42', '--rep=3', '--', 'a=42', 'b=True', 'c=foo']

    Example: storing a list::

        >>> from multiprocessor.job import Job
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
            see :class:`multiprocessor.job.Job` for details.
        typemap (Typemap):
            Controls how individual params are parsed.
        default_coercion (Coercion):
            Optional. Controls how params without a typemap entry are formatted.

    Returns:
        multiprocessor.job.Job: a runnable job with the params from this argv.

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
        <multiprocessor.job.JobResult object at 0x...>

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

    # turn meta into a dict, but coerce later
    meta = _dict_from_argv(meta_args, typemap={}, default_coercion='str')

    def _read_meta_arg(name):
        try:
            return meta.pop(name)
        except KeyError:
            raise KeyError("expected argument {} in argv".format(name))

    job_id = int(_read_meta_arg('--id'))
    repetition_id = int(_read_meta_arg('--rep'))

    if meta:
        keys = sorted(meta)
        raise TypeError("unexpected meta args: {}".format(', '.join(keys)))

    params = _dict_from_argv(param_args,
                             typemap=typemap,
                             default_coercion=default_coercion)

    return multiprocessor.job.Job(job_id, repetition_id, callback, params)

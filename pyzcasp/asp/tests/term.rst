Required imports::

    >>> from zope.interface import providedBy
    >>> from pyzcasp.asp import Term, ITerm

We start creating a ``Term`` instance with some arguments and check it provides ``ITerm``::

    >>> term1 = Term('predicate', [1,u'unicode', 'string', Term('native')])
    >>> ITerm in providedBy(term1)
    True

We can get the predicate name and its arguments by using::

    >>> term1.pred
    'predicate'
    >>> term1.args
    [1, u'"unicode"', '"string"', Term('native')]
    >>> term1.arg(0), term1.arg(1), term1.arg(2), term1.arg(3)
    (1, u'unicode', 'string', Term('native'))

``Term`` instances implement ``__str__``::

    >>> str(term1)
    'predicate(1,"unicode","string",native)'

We can also create a ``Term`` without arguments::

    >>> noargs = Term('noargs')
    >>> str(noargs)
    'noargs'
    >>> noargs.args
    []
    >>> noargs.arg(0)
    Traceback (most recent call last):
    ...
    IndexError: list index out of range

Instances of ``Term`` are comparable and hashable::

    >>> term1 == noargs
    False
    >>> term1 != noargs
    True
    >>> term2 = Term('predicate', [1,u'unicode', 'string', Term('native')])
    >>> term1 == term2
    True
    >>> hash(term1) == hash(term2) 
    True


``Term`` instances implement `__repr__`::

    >>> term1
    Term('predicate',[1,u'"unicode"','"string"',Term('native')])
    >>> noargs
    Term('noargs')


The predicate name must be a non-empty string::

    >>> noargs = Term(2)
    Traceback (most recent call last):
    ...
    TypeError: Predicate name must be string. 2 <type 'int'>

    >>> noargs = Term('')
    Traceback (most recent call last):
    ...
    ValueError: Predicate name must be a non-empty string.

Arguments cannot be neither float nor complex numbers::

    >>> novalid = Term('novalid', [1.2, complex(1,3)])
    Traceback (most recent call last):
    ...
    TypeError: Number arguments must be integers. The following arguments are forbidden: [1.2, (1+3j)]

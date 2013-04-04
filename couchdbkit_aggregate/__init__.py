from . import fn
from numbers import Number
from couchdbkit_aggregate.fn import NO_VALUE

__all__ = ['AggregateView', 'KeyView', 'IndicatorView']


class KeyView(object):
    def __init__(self, key, reduce_fn=None, startkey_fn=None, endkey_fn=None,
                 couch_view=None, db=None):
        """
        key -- the individual key/field/slug in the CouchDB map output
        reduce_fn -- reduce function for values of key (default: sum)
        startkey_fn -- see CouchView
        endkey_fn -- see CouchView
        db -- the couchdbkit Database object
        couch_view -- the view name

        If reduce_fn is an instance (or subclass) of CouchReduceFunction,
        get_value() will do a reduce query under the hood, otherwise it will do
        a map query and return reduce_fn(values).

        If db or couch_view are not specified, you must specify them when
        calling get_value().

        """
        if isinstance(reduce_fn, type):
            reduce_fn = reduce_fn()

        self.key_slug = [key] if key else []
        self.reduce_fn = reduce_fn or fn.sum()
        self.is_couch_reduce = isinstance(self.reduce_fn, fn.CouchReduceFunction)

        self.startkey_fn = startkey_fn or (lambda x: x)
        self.endkey_fn = endkey_fn or (lambda x: x + [{}])

        self.couch_view = couch_view
        self.db = db

    def get_value(self, key, startkey=None, endkey=None, couch_view=None,
                  db=None, **kwargs):
        startkey = key + self.key_slug + self.startkey_fn(startkey or [])
        endkey = key + self.key_slug + self.endkey_fn(endkey or [])

        result = (self.db or db).view(
            self.couch_view or couch_view,
            reduce=self.is_couch_reduce,
            startkey=startkey,
            endkey=endkey,
            wrapper=lambda r: r['value'],
            **kwargs)

        if self.is_couch_reduce:
            result = result.first()

        return self.reduce_fn(result)


class IndicatorView(object):
    def __init__(self, numerator_view, denominator_view, indicator_fn=None):
        """
        numerator_view -- The KeyView that will be used to calculate the numerator
        denominator_view -- The KeyView that will be used to calculate the denominator

        indicator_fn -- function used to combine the numerator and denominator. (default: (num / den) * 100
        """

        self.numerator_view = numerator_view
        self.denominator_view = denominator_view
        self.indicator_fn = indicator_fn or (lambda x, y: x * 100 / y)

    def get_value(self, key, **kwargs):
        numerator = self.numerator_view.get_value(key, **kwargs)
        denominator = self.denominator_view.get_value(key, **kwargs)
        if isinstance(numerator, Number) and isinstance(denominator, Number):
            return self.indicator_fn(numerator, denominator)
        else:
            return NO_VALUE


class KeyViewCollector(type):
    def __new__(cls, name, bases, attrs):
        attrs['key_views'] = dict((name, attr) for name, attr in attrs.items()
                                  if isinstance(attr, KeyView) or isinstance(attr, IndicatorView))

        return super(KeyViewCollector, cls).__new__(cls, name, bases, attrs)


class AggregateView(object):
    __metaclass__ = KeyViewCollector

    @classmethod
    def view(cls, key, **kwargs):
        row = {}
        for slug, key_view in cls.key_views.items():
            row[slug] = key_view.get_value(key, **kwargs)
        return row

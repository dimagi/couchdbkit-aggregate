from . import fn

__all__ = ['AggregateView', 'KeyView']

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


class KeyViewCollector(type):
    def __new__(cls, name, bases, attrs):
        attrs['key_views'] = dict((name, attr) for name, attr in attrs.items()
                                  if isinstance(attr, KeyView))

        return super(KeyViewCollector, cls).__new__(cls, name, bases, attrs)


class AggregateView(object):
    """
    When writing a CouchDB view, one way you might try to structure your map.js
    is to emit an associative array of calculated fields:

        emit([doc.user_id, doc.created_at], {foo: 1, bar: 0})

    With some work, you can create a reduce.js that sums the values for each
    field across all documents, or maybe something a little harder, like
    finding the mean.  But if you suddenly need to do something for one field
    that can't be done in a CouchDB reduction, like find the median, this
    approach fails.

    A good way to handle that is to instead do:

        emit(["foo", doc.user_id, doc.created_at], 1);
        emit(["bar", doc.user_id, doc.created_at], 0);

    That way you can do a CouchDB reduction using the builtin _stats, _count,
    or _sum views for fields where you want the sum, mean, etc. and a slower
    in-application reduction for fields where you need something more.
    
    In addition, sometimes you want to have some documents not included in the
    calculation, but only for one field, such as when a field involves
    calculations related to time and you want to exclude documents that aren't
    old enough to have a determined value for that field.

    Then you could do:

        emit(["bar", doc.user_id, doc.created_at, doc.some_date], 0);

    And add another value to your startkey and endkey.

    This module lets you define a reduce view by doing this in map.js:

        //!code util/emit_array.js
        data = {
            foo: 1,
            bar: 0,
            spam: [1, 1, 2]  // will each be emitted as separate values
        };
        emit_array([doc.user_id, doc.created_at], data, {bar: doc.some_date});

    and this in Python:

        from couchdb_aggregate import fn

        class MyView(AggregateView):
            foo = KeyView('foo')  # default reduce is built-in couchdb sum
            foo_mean = KeyView('foo', reduce_fn=fn.mean) # using _stats view
            fifth_smallest_foo = KeyView('foo,
                reduce_fn=lambda values: sorted(values)[4])
            bar = KeyView('bar', endkey_fn=lambda: today - 4)

        result = MyView.view([[user_id1], [user_id2], ...]
                             startkey=[begin_date],
                             endkey=[end_date]
                             db=my_database,
                             couch_view='app/view')

        print result
        # [ {'foo': sum of foo,         # for user_id1
             'foo_mean': average foo,
             'bar': sum of bar, but only where doc.some_date < today - 4},
            ...
          ]


    The KeyView constructor accepts db and couch_view arguments as well, so you
    can pull data from multiple views or databases into one combined view if
    you want.

    """
    __metaclass__ = KeyViewCollector

    @classmethod
    def view(cls, key, **kwargs):
        row = {}
        for slug, key_view in cls.key_views.items():
            row[slug] = key_view.get_value(key, **kwargs)
        return row

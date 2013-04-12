from . import fn
#from memoize import memoize

__all__ = ['AggregateView', 'KeyView', 'AggregateKeyView']

class KeyView(object):
    def __init__(self, key, startkey_fn=None, endkey_fn=None, couch_view=None,
                 db=None):
        """
        key -- the individual key/field/slug in the CouchDB map output
        startkey_fn -- see CouchView
        endkey_fn -- see CouchView
        db -- the couchdbkit Database object
        couch_view -- the view name

        If db or couch_view are not specified, you must specify them when
        calling get_value().

        """

        self.key_slug = [key] if key else []

        self.startkey_fn = startkey_fn or (lambda x: x)
        self.endkey_fn = endkey_fn or (lambda x: x + [{}])

        self.couch_view = couch_view
        self.db = db

    #@memoize
    def get_value(self, key, startkey=None, endkey=None, couch_view=None,
                  db=None, **kwargs):
        startkey = key + self.key_slug + self.startkey_fn(startkey or [])
        endkey = key + self.key_slug + self.endkey_fn(endkey or [])

        return (self.db or db).view(
            self.couch_view or couch_view,
            reduce=self.is_couch_reduce,
            startkey=startkey,
            endkey=endkey,
            wrapper=lambda r: r['value'],
            **kwargs)


class AggregateKeyView(object):
    def __init__(self, fn=None, *key_views):
        """
        key_views -- the KeyViews whose results to pass to the calculation
        fn -- the function to apply to the key_views

        """
        self.key_views = key_views
        self.fn = fn

    #@memoize
    def get_value(self, key, **kwargs):
        return self.fn(*[v.get_value(key, **kwargs) for v in self.key_views]) 


class ViewCollector(type):
    def __new__(cls, name, bases, attrs):
        key_views = {}

        for name, attr in attrs.items():
            if isinstance(attr, (KeyView, AggregateKeyView)):
                key_views[name] = attr
                attrs.pop(name)
                
        attrs['key_views'] = key_views

        return super(ViewCollector, cls).__new__(cls, name, bases, attrs)


class AggregateView(object):
    __metaclass__ = ViewCollector

    @classmethod
    def get_result(cls, key, **kwargs):
        result = {}

        for slug, key_view in cls.key_views.items():
            result[slug] = key_view.get_value(key, **kwargs)

        return result
